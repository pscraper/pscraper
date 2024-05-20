import re
import time
import os
from typing import Any
from utils.util_func_common import replace_to_kst, replace_specific_unicode
from utils.util_func_dotnet import extract_qnumber_from_kb_file_name
from bs4 import BeautifulSoup
from bs4 import ResultSet
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from crawler.crawling_manager import CrawlingManager
from classes.const import AppMeta, Sleep, FilePath, DirPath, FileStatus
from classes.dotnet import DotnetCommon, DotnetDOM, DotnetFormat


class DotnetCrawlingManager(CrawlingManager):
    def __init__(self, url: str, category: str):
        super().__init__(category=category, url=url)
        self.keys = self.meta["dotnet_excel_key"]

    def _get_cve_string(self) -> str:
        div = self.soup.find("div", "entry-content")
        cve_list = list(
            map(
                lambda x: re.match(DotnetDOM.CVE_STR, x.text).group(),
                div.find_all(id=re.compile(DotnetDOM.CVE_ID)),
            )
        )
        return ",".join(cve_list)

    def _get_architecture(self, file_name: str) -> str:
        architectures = ["x86", "x64", "arm64"]
        for architecture in architectures:
            if architecture in file_name:
                return architecture

        return "Undefined"

    def _search_patch_file(
        self, qnumber: str, trs: list[WebElement], main_window: str
    ) -> tuple[str, str]:
        driver = self.driver
        files = list()

        # 다운로드 버튼 클릭
        for tr in trs:
            tds = self._driver_wait_and_finds(by=By.TAG_NAME, value="td", element=tr)
            patch_title = tds[0].text

            if "Embedded" in patch_title or "Itanium" in patch_title:
                self.logger.info("Embedded 또는 Itanium 패치 제외")
                continue

            tds[-1].click()
            time.sleep(Sleep.LONG)
            self._wait_(DirPath.DOTNET, FileStatus.DOWNLOADING)

        for handle in driver.window_handles:
            if handle == main_window:
                continue

            driver.switch_to.window(handle)

            # 열린 다운로드 창에서 파일 다운로드 받기
            box = self._driver_wait_and_find(
                by=By.XPATH, value=DotnetDOM.PF_DOWNLOAD, element=driver
            )
            divs: list[WebElement] = box.find_elements(by=By.TAG_NAME, value="div")[1:]

            for div in divs:
                atag = self._driver_wait_and_find(
                    by=By.TAG_NAME, value="a", element=div
                )
                vendor_url = atag.get_attribute("href")
                if self._is_already_exists(DirPath.DOTNET, atag.text.split("_")[0]):
                    self.logger.info(f"중복된 파일 제외: {atag.text}")
                    continue

                ext_qnumber = extract_qnumber_from_kb_file_name(atag.text)
                if qnumber != ext_qnumber:
                    self.logger.info(
                        f"일치하지 않는 파일 제외: {qnumber} != {ext_qnumber}"
                    )
                    continue

                atag.click()
                file_name = atag.text
                self.logger.info("------------ [Downloading] ---------------")
                self.logger.info(file_name)
                self.logger.info(vendor_url)

                files.append(
                    {
                        "file_name": file_name,
                        "vendor_url": vendor_url,
                        "architecture": self._get_architecture(file_name),
                        "subject": file_name,
                    }
                )

            driver.close()

        return files

    def _download_patch_file(self, result, qnumbers: set[str]):
        driver = self.driver
        file_dict: dict[str, Any] = dict()

        for qnumber in qnumbers:
            common_dict = result[qnumber]["common"]
            catalog_link = common_dict["catalog_link"]
            file_dict[qnumber] = list()

            try:
                main_window = driver.current_window_handle
                driver.get(catalog_link)
                table = self._driver_wait_and_find(
                    by=By.CLASS_NAME, value="resultsBorder", element=driver
                )
                trs: list[WebElement] = table.find_elements(by=By.TAG_NAME, value="tr")[
                    1:
                ]

                # 다운로드 작업 시작 세팅
                driver.switch_to.window(main_window)
                time.sleep(Sleep.MEDIUM)
                files = self._search_patch_file(qnumber, trs, main_window)
                driver.switch_to.window(main_window)
                file_dict[qnumber] = files
                time.sleep(Sleep.MEDIUM)

                # 다운로드 완료 대기
                self._wait_(DirPath.DOTNET, FileStatus.DOWNLOADING)

            except Exception as e:
                self.logger.critical(e)
                continue

            finally:
                self._wait_(DirPath.DOTNET, FileStatus.DOWNLOADING)

        return file_dict

    # 수집할 OS 대상, QNUMBER, CATALOG URL을 미리 수집해두고 시작
    def _init_patch_data(self) -> None:
        soup = self.soup
        tbody: BeautifulSoup = soup.find("table").find("tbody")
        tds: list[BeautifulSoup] = tbody.find_all("td")

        last_product_key = ""
        last_dotnet_key = ""
        last_catalog_link = ""
        key_idx = 0

        for td in tds:
            if len(self.keys) <= key_idx:
                break

            tstrip: str = td.text.strip()
            is_parent_kb = td.find("strong") != None and tstrip.startswith("50")

            # 공란 무시
            if tstrip == "":
                continue

            # KBNumber 중 Bold 처리된 것은 부모 KBNumber이므로 무시
            if is_parent_kb:
                continue

            # Microsoft 혹은 Windows로 시작하면 Product Version을 나타냄
            if tstrip.startswith("Microsoft") or tstrip.startswith("Windows"):
                last_product_key = tstrip

            # .NET으로 시작하면 .NET 버전을 나타냄
            elif tstrip.startswith(".NET"):
                if last_product_key == "":
                    raise Exception(
                        "[ERR] 마지막으로 검색된 Product Version이 존재하지 않습니다."
                    )

                last_dotnet_key = tstrip

            # Catalog 링크 수집
            elif tstrip.startswith("Catalog"):
                href = td.findChild("a")["href"]
                last_catalog_link = href

            # 자식 KBNumber인 경우
            elif re.match("^50\d{5}", tstrip):
                if last_product_key == "" or last_dotnet_key == "":
                    raise Exception(
                        "[ERR] 마지막으로 검색된 Product Version 혹은 .NET Version이 존재하지 않습니다."
                    )

                res = input(
                    f"[{tstrip}] {last_product_key} {last_dotnet_key} -> {self.keys[key_idx]}? "
                )

                if res != "y":
                    continue

                tmp = self.keys[key_idx]
                self.keys[key_idx] = (
                    f"{tstrip}|{last_product_key}|{last_dotnet_key}|{last_catalog_link}|{tmp}\n"
                )
                key_idx += 1

        # 기존 파일 삭제 후 mapper.txt 파일 기록
        if FilePath.MAPPER.exists():
            os.remove(FilePath.MAPPER)
            self.logger.warn(f"기존 {FilePath.MAPPER.name} 파일 삭제")

        with open(FilePath.MAPPER, "w", encoding=AppMeta.ENC_TYPE) as fp:
            fp.writelines(self.keys)
            self.logger.info(f"{FilePath.MAPPER.name} 파일 초기화 완료")

    def _get_patch_date(self) -> str:
        patch_date = input("(ex. 2024/2/1) 패치 노트에 기록된 날짜를 입력해주세요: ")
        splt = patch_date.split("/")
        return "/".join([splt[0], splt[1], str(int(splt[2]) + 1)])

    def _get_severity(self) -> str:
        return input("패치의 보안 중요도를 입력해주세요: ").capitalize()

    def _get_title_and_summary(
        self, patch_date: str, category: str, qnumbers: set[str]
    ) -> dict[str, Any]:
        driver = self.driver
        ts_dict = dict()

        for qnumber in qnumbers:
            ts_dict[qnumber] = dict()

            for nation in DotnetCommon.NATION_LIST:
                ts_dict[qnumber][nation] = dict()
                bulletin_url = DotnetFormat.get_bulletin_url(nation, qnumber)

                try:
                    driver.get(bulletin_url)
                    self._driver_wait(By.ID, DotnetDOM.TS_HEADER)
                    self._driver_wait(By.ID, DotnetDOM.TS_SUMMARY)
                    time.sleep(Sleep.SHORT)
                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    title: str = replace_specific_unicode(
                        soup.find(
                            name="h1", attrs={"id": DotnetDOM.TS_HEADER}
                        ).text.strip()
                    )
                    section = soup.find(
                        name="section", attrs={"id": DotnetDOM.TS_SUMMARY}
                    )
                    ps: ResultSet[BeautifulSoup] = section.find_all(name="p")

                    summary = ""
                    for p in ps:
                        pstrip: str = p.text.strip()
                        if pstrip.startswith("CVE"):
                            summary += replace_specific_unicode(pstrip)
                            summary += "\n"

                    # Summary가 수집되지 않으면 기본 문자열을 가져온다.
                    if not summary:
                        ps = section.find_all("p")[1]
                        summary = replace_specific_unicode(ps.text[1:-1].strip())

                except Exception as e:
                    self.logger.critical(e)
                    raise e

                ts_dict[qnumber][nation]["bulletin_url"] = bulletin_url
                ts_dict[qnumber][nation]["title"] = replace_to_kst(
                    patch_date, title, category
                )
                ts_dict[qnumber][nation]["summary"] = summary

        return ts_dict

    def _del_driver(self):
        try:
            del self.driver

        except Exception as _:
            pass

        finally:
            super()._del_driver()
