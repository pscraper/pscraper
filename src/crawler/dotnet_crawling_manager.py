import re
import time
import os
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from bs4 import ResultSet
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from crawling_manager import CrawlingManager
from utils.util_func_dotnet import replace_specific_unicode
from const import (
    CVE_STR,
    CVE_ID,
    KB_STR,
    TS_HEADER,
    TS_SUMMARY,
    PF_DOWNLOAD,
    DOTNET_CAB_PATH,
    MAPPER_FILE_PATH,
    DOTNET_BULLETIN_URL_FORMAT,
    DOTNET_NATIONS_LIST,
    ENC_TYPE,
    logger
)


class DotnetCrawlingManager(CrawlingManager):
    def __init__(self, url: str, category: str):
        super().__init__(category = category, url = url)

        # cabs 폴더가 없으면 생성
        if not DOTNET_CAB_PATH.exists():
            logger.info(f"{DOTNET_CAB_PATH} 생성")
            DOTNET_CAB_PATH.mkdir()
        
        self.keys = self.meta['excel_key']
        

    # pathfiles/dotnet 폴더를 통째로 복사해서 옮기고 삭제한다.
    def _move_and_remove_dir(self):
        dst = Path.home() / "Desktop"

        if os.path.exists(dst / "dotnet"):
            shutil.rmtree(dst / "dotnet")

        shutil.move(self._patch_file_path, dst)
        shutil.copy(self._data_file_path / "result.json", dst / "dotnet" / "result.json")


    def _extract_file_info(self, file_dict):
        for qnumber in file_dict:
            for info in file_dict[qnumber]:
                file_name = info["file_name"]
                
                self.logger.info(f"{file_name} 압축 해제")
                cab_file_name = self._unzip_msu_file(file_name)
                file_size, md5, sha256 = self._extract_file_hash(file_name)

                info.update({
                    "file_size": file_size,
                    "MD5": md5,
                    "SHA256": sha256,
                    "WSUS 파일": cab_file_name
                })
        
        # 불필요한 파일 삭제
        for file in self._cab_file_path.iterdir():
            if file.name.endswith("_WSUSSCAN.cab"):
                continue
            
            # 관리자 권한이 아닌 경우 임시 파일을 삭제하려다 엑세스 거부 예외가 발생할 수 있음 
            if file.name.endswith(".tmp"):
                continue

            os.remove(self._cab_file_path / file)
            self.logger.info(f"[Delete] {self._cab_file_path / file}")

    
    def _unzip_msu_file(self, file_name: str) -> str:
        file_abs_path = self._patch_file_path / file_name
        cab_file_name = file_name.split(".msu")[0] + "_WSUSSCAN.cab" 
        cmd = f"expand -f:* {file_abs_path} {self._cab_file_path}"
        
        try:
            os.system(cmd)
            self._wait_til_tmp_folder_exists()
            Path.rename(self._cab_file_path / "WSUSSCAN.cab", self._cab_file_path / cab_file_name)
        
        except FileExistsError as e:    
            self.logger.warning("msu 파일 압축 해제 과정에서 에러 발생")
            self.logger.warning(e)
            
        return cab_file_name
    
    
    
    def _extract_file_hash(self, file_name: str) -> tuple[str, str, str]:
        file_abs_path = self._patch_file_path / file_name

        with open(file_abs_path, "rb") as fp:
            binary = fp.read()
        
        md5 = hashlib.md5(binary).hexdigest()
        sha256 = hashlib.sha256(binary).hexdigest()
        size_tmp = f"{float(os.path.getsize(file_abs_path)) / (2 ** 20):.1f}"

        return size_tmp, md5, sha256
        
        

    def _get_cve_string(self) -> str:
        div = self.soup.find("div", "entry-content")
        cve_list = list(map(lambda x: re.match(CVE_STR, x.text).group(), div.find_all(id = re.compile(CVE_ID))))
        return ",".join(cve_list)
    


    def _get_architecture(self, file_name: str) -> str:
        architectures = ["x86", "x64", "arm64"]

        for architecture in architectures:
            if architecture in file_name:
                return architecture
            
        return "Undefined"
    
    
    
    def _search_patch_file(self, trs: list[WebElement], main_window: str) -> tuple[str, str]:
        driver = self.driver
        files = list()

        # 다운로드 버튼 클릭
        for tr in trs:
            self._driver_wait(By.TAG_NAME, "td")
            tds: list[WebElement] = tr.find_elements(by = By.TAG_NAME, value = "td")[1:]
            patch_title = tds[0].text

            if "Embedded" in patch_title or "Itanium" in patch_title:
                logger.info("Embedded 또는 Itanium 패치 제외")
                continue
            
            tds[-1].click()
            time.sleep(2)

        for handle in driver.window_handles:
            if handle == main_window:
                continue

            driver.switch_to.window(handle)

            # 열린 다운로드 창에서 파일 다운로드 받기
            self._driver_wait(By.XPATH, PF_DOWNLOAD)
            box: WebElement = driver.find_element(by = By.XPATH, value = PF_DOWNLOAD)
            divs: list[WebElement] = box.find_elements(by = By.TAG_NAME, value = "div")[1:]

            for div in divs:
                atag: WebElement = div.find_element(by = By.TAG_NAME, value = "a")
                vendor_url = atag.get_attribute('href')
                
                time.sleep(2)
                
                if self._is_already_exists(atag.text.split("_")[0]):
                    logger.info(f"중복된 파일 제외: {atag.text}")
                    continue
                
                time.sleep(2)
                
                atag.click()
                file_name = self._msu_file_name_change(atag.text)
                logger.info("------------ [Downloading] ---------------")
                logger.info(f"파일명: {file_name}")
                logger.info(f"Vendor URL: {vendor_url}")

                file = {   
                    "file_name": file_name,
                    "vendor_url": vendor_url,
                    "architecture": self._get_architecture(file_name),
                    "subject": file_name
                }                
                
                files.append(file)
                
            driver.close()

        return files



    def _download_patch_file(self, result, qnumbers: set[str]):
        driver = self.driver
        file_dict: dict[str, list[dict[str, str]]] = dict()
        
        for qnumber in qnumbers:
            common_dict = result[qnumber]['common']
            catalog_link = common_dict['catalog_link']

            file_dict[qnumber] = list()

            try:
                driver.get(catalog_link)
                self._driver_wait(By.CLASS_NAME, "resultsBorder")
                main_window = driver.current_window_handle
                table: WebElement = driver.find_element(by = By.CLASS_NAME, value = "resultsBorder")
                trs: list[WebElement] = table.find_elements(by = By.TAG_NAME, value = "tr")[1:]

                # 다운로드 작업 시작 세팅
                driver.switch_to.window(main_window)
                time.sleep(2)
                files = self._search_patch_file(trs, main_window)
                driver.switch_to.window(main_window)

                file_dict[qnumber] = files
                time.sleep(2)
 
                # 다운로드 완료 대기 
                self._wait_til_download_ended()

            except Exception as e:
                logger.critical(e)
                continue
            
            finally:
                self._wait_til_download_ended()

        
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
                    raise Exception("[ERR] 마지막으로 검색된 Product Version이 존재하지 않습니다.")
                
                last_dotnet_key = tstrip

            # Catalog 링크 수집
            elif tstrip.startswith("Catalog"):
                href = td.findChild("a")['href']
                last_catalog_link = href
            
            # 자식 KBNumber인 경우
            elif re.match("^50\d{5}", tstrip):
                if last_product_key == "" or last_dotnet_key == "":
                    raise Exception("[ERR] 마지막으로 검색된 Product Version 혹은 .NET Version이 존재하지 않습니다.")
                
                res = input(f"[{tstrip}] {last_product_key} {last_dotnet_key} -> {self.keys[key_idx]}? ")
                
                if res != 'y':
                    continue
                
                tmp = self.keys[key_idx] 
                self.keys[key_idx] = f"{tstrip}|{last_product_key}|{last_dotnet_key}|{last_catalog_link}|{tmp}\n" 
                key_idx += 1
        
        # 기존 파일 삭제 후 mapper.txt 파일 기록
        if MAPPER_FILE_PATH.exists():
            logger.warn(f"기존 {MAPPER_FILE_PATH.name} 파일 삭제")
            os.remove(MAPPER_FILE_PATH)
        
        with open(MAPPER_FILE_PATH, "w", encoding = ENC_TYPE) as fp:
            fp.writelines(self.keys)
            logger.info(f"{MAPPER_FILE_PATH.name} 파일 초기화 완료")
                


    # TODO 패치 일자 긁어오기
    def _get_patch_date(self) -> str:
        date_elem = self.soup.find("em").find("strong")
        
        if date_elem == None:
            logger.warn("PatchDate 정보를 찾을 수 없어 현재 날짜를 반환합니다.")
            return datetime.today().strftime("%Y/%m/%d")
            
        # date = date_elem.text[1:-1].strip().split("/")
        # return f"{date[-1]}/{date[0]}/{int(date[1]) + 1}"
        return datetime.today().strftime("%Y/%m/%d")



    def _get_title_and_summary(self, qnumbers: set[str]):
        driver = self.driver
        ts_dict = dict()
        
        for qnumber in qnumbers:
            ts_dict[qnumber] = dict()
            
            for nation in DOTNET_NATIONS_LIST:
                ts_dict[qnumber][nation] = dict()
                bulletin_url = DOTNET_BULLETIN_URL_FORMAT.format(nation, qnumber)

                try:
                    driver.get(bulletin_url)
                    self._driver_wait(By.ID, TS_HEADER)
                    self._driver_wait(By.ID, TS_SUMMARY)
                    time.sleep(1)

                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    title: str = soup.find(name = "h1", attrs = {"id": TS_HEADER}).text.strip()
                    section = soup.find(name = "section", attrs = {"id": TS_SUMMARY})  
                    ps: ResultSet[BeautifulSoup] = section.find_all(name = "p")
            
                    summary = ""
                    for p in ps:
                        pstrip: str = p.text.strip()
                        if pstrip.startswith("CVE"):
                            summary += replace_specific_unicode(pstrip)
                    
                    # Summary가 수집되지 않으면 기본 문자열을 가져온다.
                    if not summary:
                        ps = section.find_all("p")[1]
                        summary = replace_specific_unicode(ps.text[1:-1].strip())

                except Exception as _:
                    pass
                
                ts_dict[qnumber][nation]['bulletin_url'] = bulletin_url
                ts_dict[qnumber][nation]['title'] = title
                ts_dict[qnumber][nation]['summary'] = summary
                
        
        return ts_dict
    
    

    def _del_driver(self):
        try:
            del self.qnumbers
            del self.patch_info_dict
            del self.error_patch_dict
            del self.driver
            del self.dotnet

        except Exception as _:
            pass

        finally:
            super()._del_driver()


    def _msu_file_name_change(self, name: str) -> str:
        splt = name.split("_")
        
        # ndp가 안붙은 파일의 경우
        if splt[0].find("ndp") == -1:
            qnumber = name[name.find("kb") + 2:name.rfind("-")]
            dotnet_version = self.qnumbers[qnumber][1]

            if "4.8" in dotnet_version:
                tmp = "48"
            elif "4.8.1" in dotnet_version:
                tmp = "481"
            else:
                tmp = "472"

            splt[0] = splt[0] + "-ndp" + tmp

            self.logger.info(f"[No ndp] {qnumber} {dotnet_version}")
            self.logger.info(f" -> {splt[0].replace('kb', 'KB') + '.msu'}")

        return splt[0].replace("kb", "KB") + ".msu" 
    