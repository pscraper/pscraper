import sys
import re
import time
import os
import hashlib
import shutil
from pathlib import Path
from bs4 import BeautifulSoup
from bs4 import ResultSet
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from datetime import datetime
from crawling_manager import CrawlingManager
from classes import Category
from const import (
    logger,
    DOTNET_FILE_PATH,
    DOTNET_CAB_PATH
)


class DotnetCrawlingManager(CrawlingManager):
    def __init__(self, url: str):
        super().__init__(category = str(Category.DOTNET.name), url = url)
        self.name = __class__.__name__

        if not DOTNET_CAB_PATH.exists():
            logger.info(f"[{self.name}] {DOTNET_CAB_PATH} 생성")
            DOTNET_CAB_PATH.mkdir()


    def run(self) -> None:
        try:
            # 패치 대상 데이터 초기화
            qnumbers, patch_info_dict = self._init_patch_data()
            
            # 프롬프트 출력, 패치 대상 데이터 최종 결정(제거)
            self._show_prompt(patch_info_dict)
            
            # 프롬프트 창 clear
            os.system("cls")

            # 패치 날짜 정보 가져오기 (TODO 문서마다 다름)
            patch_date = datetime.today().strftime("%Y/%m/%d") # self._get_patch_date()
            self.logger.info(f"[Patch Date] {patch_date}")

            # 패치 CVE 문자열 가져오기
            # 이 이후로 soup 객체를 사용하지 않으므로 메모리 해제
            cve_string = self._get_cve_string()
            self.logger.info(f"[CVE List] {cve_string}")
            del self.soup

            # BulletinID, KBNumber, PatchDate, CVE, 중요도 정보 가져오기
            # TODO 중요도 정보 가져오기 (MSRC)s
            common_dict = self._get_common_info(patch_date, cve_string)
            self.logger.info("[Common Info]")

            for qnumber in common_dict:
                self.logger.info(f"[{qnumber}]")

                for key, val in common_dict[qnumber].items():
                    self.logger.info(f"\t- {key}: {val}")
                
            # 패치 대상의 각 카탈로그 링크에서 패치 파일 다운로드
            # 각 패치 파일 이름과 vendor URL에 대한 Dict 반환
            file_dict = self._download_patch_file(common_dict, cve_string)
            self._wait_til_download_ended()
            time.sleep(2)

            # msu 파일 압축 해제, WSUSSCAN 파일명 변경 작업, file_dict 업데이트
            self._extract_file_info(file_dict)

            # 각 언어별 bulletin URL에서 제목과 요약 수집
            title_and_summary = self._get_title_and_summary(file_dict, cve_string)

            # 모든 파일이 정상적으로 존재하는지 검증
            self._check_msu_and_cab_file_exists()

            # 모든 QNumber에 대해 수집되었는지 검증
            self._check_all_qnumber_file_exists()

            # 모든 검증이 끝나면 최종 JSON 파일 생성
            self._make_result_file(common_dict, file_dict, title_and_summary)

            os.system("cls")
            print("프로그램이 정상적으로 종료되었습니다")
            print("바탕화면으로 패치 파일과 결과 정보 파일을 이동하였습니다.")
            print("result.json 파일을 열어 불필요한 유니코드 문자를 제거해주세요.")
            print("Title과 패치 날짜를 KST 기준으로 변경해주세요.")
        
        except Exception as e:
            self._error_report(e, self.error_patch_dict)

        finally:
            self._del_driver()


    # 에러 발생 시 다운로드한 모든 패치 파일을 삭제한다.
    def _remove_all_files(self):
        shutil.rmtree(self._patch_file_path)
        self.logger.warning("에러가 발생하여 모든 패치 파일을 제거하였습니다.")


    # pathfiles/dotnet 폴더를 통째로 복사해서 옮기고 삭제한다.
    def _move_and_remove_dir(self):
        dst = Path.home() / "Desktop"

        if os.path.exists(dst / "dotnet"):
            shutil.rmtree(dst / "dotnet")

        shutil.move(self._patch_file_path, dst)
        shutil.copy(self._data_file_path / "result.json", dst / "dotnet" / "result.json")


    def _make_result_file(self, common_dict, file_dict, title_and_summary):
        save_path = self._data_file_path / "result.json"
        kb_reg = self.dotnet['re']['kb']
        result = dict()
        qnums = self.qnumbers.keys()

        for qnum in qnums:
            if qnum not in result:
                result[qnum] = dict()

            result[qnum]["common"] = common_dict[qnum]
            result[qnum]['files'] = list()
            result[qnum]['nations'] = dict()

            for file in file_dict[qnum]:
                # 가끔 파일명 내 QNumber와 실제 수집하려한 QNumber가 불일치하는 상황이 있음
                fname = re.match(kb_reg, file['file_name'][13:])
                
                if fname == None:
                    result[qnum]['files'].append(file)
                else:
                    real_qnum = fname[2:]
                    if real_qnum not in result:
                        result[real_qnum] = dict()

                    result[real_qnum]['files'].append(file)

            for nation in title_and_summary[qnum]:
                result[qnum]['nations'][nation] = title_and_summary[qnum][nation]
                
        self._save_result(save_path, result)


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
    
    
    def _wait_til_tmp_folder_exists(self):
        while True:
            tmp = False
            
            for path in os.listdir(self._cab_file_path):
                if path.endswith(".tmp"):
                    tmp = True
                    break
                    
            if not tmp:
                time.sleep(2)
                break
                    

    def _extract_file_hash(self, file_name: str) -> tuple[str, str, str]:
        file_abs_path = self._patch_file_path / file_name

        with open(file_abs_path, "rb") as fp:
            binary = fp.read()
        
        md5 = hashlib.md5(binary).hexdigest()
        sha256 = hashlib.sha256(binary).hexdigest()
        size_tmp = f"{float(os.path.getsize(file_abs_path)) / (2 ** 20):.1f}"

        return size_tmp, md5, sha256
        

    def _get_cve_string(self) -> str:
        cve_id_reg = self.dotnet['re']['cve_id']
        cve_reg = self.dotnet['re']['cve']
        div = self.soup.find("div", "entry-content")

        cve_list = list(map(lambda x: re.match(cve_reg, x.text).group(), div.find_all(id = re.compile(cve_id_reg))))
        return ",".join(cve_list)
    

    def _get_architecture(self, file_name: str) -> str:
        architectures = ["x86", "x64", "arm64"]

        for architecture in architectures:
            if architecture in file_name:
                return architecture
            
        return "Undefined"


    def _get_max_severity(self, severity_set: set[str], cve_string: str):
        # 빈 문자열 False 반환
        if not cve_string:
            return "Moderate"

        severities = ["critical", "important", "moderate"]

        for severity in severities:
            if severity in severity_set or severity.capitalize() in severity_set:
                return severity

        if "n/a" in severity_set or "N/A" in severity_set:
            return "Moderate"
        
        return "Low"
    

    def _search_severity(self, trs: list[WebElement], main_window: str) -> set[str]:
        driver = self.driver
        severity_set = set()

        # 중요도 조사
        for tr in trs:
            self._driver_wait(By.TAG_NAME, "td")
            tds: list[WebElement] = tr.find_elements(by = By.TAG_NAME, value = "td")[1:]
            patch_title_elem = tds[0]
            patch_title = patch_title_elem.text

            if "Embedded" in patch_title or "Itanium" in patch_title:
                continue

            patch_title_elem.click()
            time.sleep(2)

        for handle in driver.window_handles:
            if handle == main_window:
                continue
            
            driver.switch_to.window(handle)
            
            title_xpath = self.dotnet['xpath']['title']
            self._driver_wait(by = By.XPATH, name = title_xpath)
            patch_title = driver.find_element(by = By.XPATH, value = title_xpath).text
            
            severity_xpath = self.dotnet['xpath']['severity']
            self._driver_wait(by = By.XPATH, name = severity_xpath)
            severity = driver.find_element(by = By.XPATH, value = severity_xpath).text
            severity_set.add(severity)

            self.logger.info(f"[Patch Titke] {patch_title}")
            self.logger.info(f"[Severity] {severity}")
            
            driver.close()

        return severity_set
    
    
    def _search_patch_file(self, trs: list[WebElement], main_window: str) -> tuple[str, str]:
        driver = self.driver

        # 다운로드 버튼 클릭
        for tr in trs:
            self._driver_wait(By.TAG_NAME, "td")
            tds: list[WebElement] = tr.find_elements(by = By.TAG_NAME, value = "td")[1:]
            patch_title = tds[0].text

            if "Embedded" in patch_title or "Itanium" in patch_title:
                continue
            
            tds[-1].click()
            time.sleep(2)

        for handle in driver.window_handles:
            if handle == main_window:
                continue

            driver.switch_to.window(driver.window_handles[-1])

            # 열린 다운로드 창에서 파일 다운로드 받기
            xpath = self.dotnet['xpath']['download']
            self._driver_wait(By.XPATH, xpath)
            
            box: WebElement = driver.find_element(by = By.XPATH, value = xpath)
            divs: list[WebElement] = box.find_elements(by = By.TAG_NAME, value = "div")[1:]

            for div in divs:
                atag: WebElement = div.find_element(by = By.TAG_NAME, value = "a")
                vendor_url = atag.get_attribute('href')
                
                if self._is_already_exists(atag.text.split("_")[0]):
                    self.logger.info("\t[INFO] 중복된 파일 제외")
                    self.logger.info(f"\t{atag.text}")
                    continue
                
                time.sleep(1)
                atag.click()
                file_name = self._msu_file_name_change(atag.text)

                self.logger.info("------------ [Downloading] ---------------")
                self.logger.info(f"\t[파일명] {file_name}")
                self.logger.info(f"\t[Vendor URL] {vendor_url}")

            driver.close()

        return file_name, vendor_url


    def _download_patch_file(self, common_dict: dict[str, dict[str, str]], cve_string: str) -> dict[str, list[dict[str, str]]]:
        driver = self.driver
        file_dict: dict[str, list[dict[str, str]]] = dict()
        
        for qnumber, value in self.qnumbers.items():
            product_version = value[0]
            dotnet_version = value[1]
            catalog_elem = value[2]

            file_dict[qnumber] = list()
            self.error_patch_dict[qnumber] = list()            

            try:
                link = str(catalog_elem['href'])
                driver.get(link)
                self._driver_wait(By.CLASS_NAME, "resultsBorder")
                main_window = driver.current_window_handle

                table: WebElement = driver.find_element(by = By.CLASS_NAME, value = "resultsBorder")
                trs: list[WebElement] = table.find_elements(by = By.TAG_NAME, value = "tr")[1:]

                os.system("cls")

                self.logger.info(f"[{product_version} {dotnet_version}] 다운로드 작업 시작")
                self.logger.info(f"Vendor URL: {link}")

                # 중요도 조사
                severity_set = self._search_severity(trs, main_window)
                    
                # CVE가 없으면 기본 보안 등급 Moderate 적용
                max_severity = self._get_max_severity(severity_set, cve_string)
                common_dict[qnumber].update({"중요도": max_severity})

                # 다운로드 작업 시작 세팅
                time.sleep(2)
                driver.switch_to.window(main_window)

                file_name, vendor_url = self._search_patch_file(trs, main_window)

                file_info = {   
                    "file_name": file_name,
                    "vendor_url": vendor_url,
                    "product": product_version,
                    "architecture": self._get_architecture(file_name),
                    "subject": file_name
                }

                file_dict[qnumber].append(file_info)
                time.sleep(2)
 
                # 다시 main window로 전환 (카탈로그 창)
                driver.switch_to.window(main_window)
                
                # 다운로드 완료 대기 
                self._wait_til_download_ended()

            except Exception as e:
                self.logger.warning(f"{link}를 처리하던 중 에러가 발생했습니다.")
                self.logger.warning(e)

                self.error_patch_dict[qnumber].append({
                    "product": product_version,
                    "version": dotnet_version,
                    "catalog": link,
                    "message": e
                })

                continue
            
            finally:
                self._wait_til_download_ended()

        # msu 파일명 전부 변경
        self._remove_hash_from_file_name()        

        return file_dict


    def _remove_hash_from_file_name(self):
        self.logger.info(".msu 파일명에서 해시값 제거")

        for file in self._patch_file_path.iterdir():
            if not file.name.endswith(".msu"):
                continue

            renamed = self._msu_file_name_change(file.name)

            if file.name != renamed:
                try:
                    os.rename(self._patch_file_path / file.name, self._patch_file_path / renamed)
                    print(f"\t{file.name} -> {renamed}")

                except FileExistsError as e:
                    self.logger.warning("[INFO] 중복된 파일 삭제합니다")
                    self.logger.warning(f"[ERR] {e}")
                    self.logger.warning(file.name)
                    os.remove(self._patch_file_path / file.name)
                    continue


    # 수집할 OS 대상, QNUMBER, CATALOG URL을 미리 수집해두고 시작
    def _init_patch_data(self) -> tuple[dict[str, tuple[str, str, BeautifulSoup]], dict[str, list[tuple[str, str]]]]:
        '''
        Return: 
        tuple[qnumbers, patch_info_dict]
            - qnumbers: 
                - key: QNumber
                - val: tuple of product version, .NET version, catalog link
            
            - patch_info_dict
                - key: product version
                - val: list of tuple (.NET version, QNumber)
        '''
        
        soup = self.soup
        patch_info_dict: dict[str, list] = dict()
        qnumbers: dict[str, tuple[str, str, BeautifulSoup]] = dict()
        tbody: BeautifulSoup = soup.find("table").find("tbody")
        tds: list[BeautifulSoup] = tbody.find_all("td") 
        
        last_product_key = ""
        last_dotnet_key = ""
        last_catalog_link = ""
        
        for td in tds:
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
                patch_info_dict[tstrip] = list()
                last_product_key = tstrip 
            
            # .NET으로 시작하면 .NET 버전을 나타냄
            elif tstrip.startswith(".NET"):
                if last_product_key == "":
                    raise Exception("[ERR] 마지막으로 검색된 Product Version이 존재하지 않습니다.")
                
                last_dotnet_key = tstrip

            # Catalog 링크 수집
            elif tstrip.startswith("Catalog"):
                href = td.findChild("a")
                last_catalog_link = href
            
            # 자식 KBNumber인 경우
            elif re.match("^50\d{5}", tstrip):
                if last_product_key == "" or last_dotnet_key == "":
                    raise Exception("[ERR] 마지막으로 검색된 Product Version 혹은 .NET Version이 존재하지 않습니다.")
                
                if tstrip not in qnumbers:
                    qnumbers[tstrip] = (last_product_key, last_dotnet_key, last_catalog_link)
                    patch_info_dict[last_product_key].append((last_dotnet_key, tstrip))

        # 빈 Product Version 삭제
        tmp = list()
        for product in patch_info_dict:
            if len(patch_info_dict[product]) == 0:
                tmp.append(product)
        
        for product in tmp:
            del patch_info_dict[product]
            
        return qnumbers, patch_info_dict
        

    def _remove_patch(self, removed: str):
        if removed not in self.qnumbers:
            print(f"[{removed}] 목록에 없는 QNumber 입니다.")
            return

        info = self.qnumbers[removed]
        product_version = info[0]
        dotnet_version = info[1]
        tmp = list()

        for tup in self.patch_info_dict[product_version]:
            if tup[1] == removed:
                self.patch_info_dict[product_version].remove((dotnet_version, removed))

                if len(self.patch_info_dict[product_version]) == 0:
                    tmp.append(product_version)

        for t in tmp:
            del self.patch_info_dict[t]

        del self.qnumbers[removed]


    def _show_prompt(self, patch_info_dict: dict[str, list]) -> None:
        while True:
            print("\n\n-------------------- 패치 대상 정보가 수집되었습니다 ----------------------")
            for product in patch_info_dict:
                print(product)
                for data in patch_info_dict[product]:
                    version = data[0]
                    qnumber = data[1]
                    print(f"\t[{qnumber}] {version}")
                print()
            print("------------------------------------------------------------------------\n\n")

            res = input("제외할 패치의 QNumber를 입력해주세요. (여러개인 경우 ','로 구분하여 입력하고 없으면 'n' 입력) : ")

            if res == 'n':
                break

            for removed in res.split(","):
                print(f"[removed] {removed.strip()} 삭제")
                self._remove_patch(removed.strip())


    def _get_patch_date(self) -> str:
        date_elem = self.soup.find("em").find("strong")
        
        if date_elem == None:
            raise Exception("패치 날짜 정보를 가져올 수 없습니다.")
        
        date = date_elem.text[1:-1].strip().split("/")
        return f"{date[-1]}/{date[0]}/{int(date[1]) + 1}"


    def _get_title_and_summary(self, file_dict, cve_string: str) -> dict[str, dict[str, str]]:
        tmp = dict()

        driver = self.driver
        nations = self.dotnet['common']['nations']
        bulletin = self.dotnet['common']['bulletin']
        
        for qnumber in file_dict:
            tmp[qnumber] = dict()
            err = False
            
            for nation in nations:
                if err:
                    self.logger.warning(f"[warning] {qnumber}에 대한 Title, Summary 정보 수집 실패")
                    continue

                try:
                    bulletin_url = bulletin.format(nation, qnumber)
                    driver.get(bulletin_url)

                    header = self.dotnet['id']['header']
                    summary = self.dotnet['id']['summary']

                    self._driver_wait(By.ID, header)
                    self._driver_wait(By.ID, summary)
                    time.sleep(1)

                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    title: str = soup.find(name = "h1", attrs = {"id": header}).text.strip()
                    section = soup.find(name = "section", attrs = {"id": summary})   # 없는 경우도 존재
                    ps: ResultSet[BeautifulSoup] = section.find_all(name = "p")
            
                    summary = ""
                    for p in ps:
                        pstrip: str = p.text.strip()
                        if pstrip.startswith("CVE"):
                            summary += pstrip.replace(u"\u2013", "-")

                    # CVE가 없는 Cumulative 패치는 요약을 따로 가져온다.
                    if not cve_string and not summary:
                        ps = section.find_all("p")[1]
                        summary = ps.text[1:-1].strip()
                    
                    tmp[qnumber][nation] = dict()
                    tmp[qnumber][nation]["bulletin_url"] = bulletin_url 
                    tmp[qnumber][nation]["title"] = title
                    tmp[qnumber][nation]["summary"] = summary

                except Exception as _:
                    self.logger.warning(f"{qnumber}에 대한 summary를 가져오지 못했습니다.")
                    err = True

                finally:
                    if not err:
                        self.logger.info(bulletin_url)
                        self.logger.info(title)
                        self.logger.info(summary)

        return tmp


    def _check_msu_and_cab_file_exists(self):
        # cab 파일과 msu 파일이 모두 있는지 검사
        for file in os.listdir(self._patch_file_path):
            
            if not file.endswith(".msu"):
                continue

            splt = file.split("-")

            tmp = "-".join([splt[1], splt[2], splt[3]]).replace(".msu", "")
            flag = False

            for cab in os.listdir(self._cab_file_path):
                if tmp in cab:
                    self.logger.info(f"{tmp} -> {cab} 확인")
                    flag = True
                    break
           
            if not flag:
                raise Exception(f"{tmp}에 대한 cab 파일이 확인되지 않습니다.")
            

    def _check_all_qnumber_file_exists(self):
        qnumbers = set(self.qnumbers.keys())
        file_qnumbers = set()

        for file in os.listdir(self._patch_file_path):
            if not file.endswith(".msu"):
                continue

            qnumber = file.split("-")[1][2:]
            file_qnumbers.add(qnumber)

            if qnumber not in qnumbers:
                raise Exception(f"[{qnumber}] 대상 QNumber 포함되지 않은 패치 파일입니다.")

        # 교집합의 여집합이 0개가 되어야 한다.
        diff = file_qnumbers.difference(qnumbers & file_qnumbers)

        if len(diff) != 0:
            raise Exception(f"[{diff}] 수집되지 않은 QNumber가 존재합니다.")

    
    def _get_common_info(self, patch_date: str, cve_string: str) -> dict[str, dict[str, str]]:
        tmp = dict()

        for qnumber in self.qnumbers:
            tmp[qnumber] = {
                "KBNumber": f"KB{qnumber}",
                "BulletinID": f"MS-KB{qnumber}",
                "cve": cve_string,
                "PatchDate": patch_date
            }
        
        return tmp
    

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
    

if __name__ == "__main__":
    dcm = DotnetCrawlingManager("http://www.naver.com")
    dcm.run()