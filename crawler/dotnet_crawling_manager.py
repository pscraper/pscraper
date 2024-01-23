from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent))

import re
import time
import os
import hashlib
import shutil
import yaml
from crawling_manager import CrawlingManager
from bs4 import BeautifulSoup
from bs4 import ResultSet
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from datetime import datetime



class DotnetCrawlingManager(CrawlingManager):
    def __init__(self):
        super().__init__()
        
        self._cab_file_path = self._patch_file_path / "cabs"
        self.qnumbers: dict[str, tuple[str, str, BeautifulSoup]] = dict()
        self.patch_info_dict: dict[str, list[tuple(str, str)]] = dict()
        self.error_patch_dict: dict[str, list[dict[str, str]]] = dict()


    def _msu_file_name_change(self, name: str) -> str:
        splt = name.split("_")
        
        # ndp가 안붙은 파일의 경우
        if splt[0].find("ndp") == -1:
            qnumber = name[name.find("kb") + 2:name.rfind("-")]
            dotnet_version = self.qnumbers[qnumber][1]

            print(f"[No ndp] {qnumber} {dotnet_version}", end="")
            
            tmp = ""
            if "4.8" in dotnet_version:
                tmp = "48"
            elif "4.8.1" in dotnet_version:
                tmp = "481"
            else:
                tmp = "472"

            splt[0] = splt[0] + "-ndp" + tmp
            print(f" -> {splt[0].replace('kb', 'KB') + '.msu'}")

        return splt[0].replace("kb", "KB") + ".msu" 
    

    def _extract_file_info(self, file_dict):
        for qnumber in file_dict:
            for info in file_dict[qnumber]:
                file_name = info["file_name"]
                
                print(f"\n[INFO] {file_name} 압축 해제")
                cab_file_name = self._unzip_msu_file(file_name)

                time.sleep(2)

                print(f"\n[INFO] {file_name} 해시값 추출")
                file_size, md5, sha256 = self._extract_file_hash(file_name)

                info.update({
                    "file_size": file_size,
                    "MD5": md5,
                    "SHA256": sha256,
                    "WSUS 파일": cab_file_name
                })
        
        print(file_dict)

        # 불필요한 파일 삭제
        for file in os.listdir(self._cab_file_path):
            if file.endswith("_WSUSSCAN.cab"):
                continue
            
            # 관리자 권한이 아닌 경우 임시 파일을 삭제하려다 엑세스 거부 예외가 발생할 수 있음 
            if file.endswith(".tmp"):
                continue

            os.remove(self._cab_file_path / file)
            print(f"[Delete] {self._cab_file_path / file}")

    
    def _unzip_msu_file(self, file_name: str) -> str:
        file_abs_path = self._patch_file_path / file_name

        if not os.path.exists(self._cab_file_path):
            os.mkdir(self._cab_file_path)

        # msu 파일 압축해제 (WSUSSCAN 파일만)
        cmd = f"expand -f:* {file_abs_path} {self._cab_file_path}"
        os.system(cmd)
        time.sleep(3)

        try:
            cab_file_name = file_name.split(".msu")[0] + "_WSUSSCAN.cab"
            os.rename(self._cab_file_path / "WSUSSCAN.cab", self._cab_file_path / cab_file_name)
        
        except FileExistsError as e:    
            print(e)
            return "err"

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
        cve_list = list(map(lambda x: re.match("CVE-\d+-\d+", x.text).group(), div.find_all(id = re.compile("^cve"))))
        return ",".join(cve_list)
    

    def _get_architecture(self, file_name: str) -> str:
        if "x86" in file_name:
            return "x86"
        
        elif "x64" in file_name:
            return "x64"
        
        elif "arm64" in file_name:
            return "arm64"
        
        return "undefined"


    def _download_patch_file(self, common_dict: dict[str, dict[str, str]]) -> dict[str, list[dict[str, str]]]:
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

                print(f"[{product_version} {dotnet_version}] 다운로드 작업 시작")
                print("[link]", link)

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
                    
                    title_xpath = "//*[@id=\"ScopedViewHandler_titleText\"]"
                    self._driver_wait(by = By.XPATH, name = title_xpath)
                    patch_title = driver.find_element(by = By.XPATH, value = title_xpath).text
                    
                    severity_xpath = "//*[@id=\"ScopedViewHandler_msrcSeverity\"]"
                    self._driver_wait(by = By.XPATH, name = severity_xpath)
                    severity = driver.find_element(by = By.XPATH, value = severity_xpath).text
                    severity_set.add(severity)

                    print(f"[Patch Titke] {patch_title}")
                    print(f"[Severity] {severity}")
                    
                    driver.close()
                    
                # 중요도 업데이트
                max_severity = ""
                if "Critical" in severity_set or "critical" in severity_set:
                    max_severity = "Critical"
                
                elif "Important" in severity_set or "important" in severity_set:
                    max_severity = "Important"

                common_dict[qnumber].update({"중요도": max_severity})

                # 다운로드 작업 시작 세팅
                time.sleep(3)

                driver.switch_to.window(main_window)

                # 다운로드 버튼 클릭
                for tr in trs:
                    self._driver_wait(By.TAG_NAME, "td")
                    tds: list[WebElement] = tr.find_elements(by = By.TAG_NAME, value = "td")[1:]
                    patch_title = tds[0].text

                    if "Embedded" in patch_title or "Itanium" in patch_title:
                        continue
                    
                    tds[-1].click()
                    time.sleep(2)
        
                # 다운로드 수행
                for handle in driver.window_handles:
                    if handle == main_window:
                        continue

                    driver.switch_to.window(driver.window_handles[-1])

                    # 열린 다운로드 창에서 파일 다운로드 받기
                    xpath = "//*[@id=\"downloadFiles\"]"
                    self._driver_wait(By.XPATH, xpath)
                    
                    box: WebElement = driver.find_element(by = By.XPATH, value = xpath)
                    divs: list[WebElement] = box.find_elements(by = By.TAG_NAME, value = "div")[1:]

                    for div in divs:
                        atag: WebElement = div.find_element(by = By.TAG_NAME, value = "a")
                        vendor_url = atag.get_attribute('href')
                        
                        if self._is_already_exists(atag.text.split("_")[0]):
                            print("\n\t[INFO] 중복된 파일 제외")
                            print(f"\t{atag.text}")
                            continue
                        
                        time.sleep(1)

                        atag.click()

                        file_name = self._msu_file_name_change(atag.text)

                        print("\n\t------------ [Downloading] ---------------")
                        print(f"\t[파일명] {file_name}")
                        print(f"\t[Vendor URL] {vendor_url}")
                        print("\t--------------------------------------------\n")

                        file_dict[qnumber].append({
                            "file_name": file_name,
                            "vendor_url": vendor_url,
                            "product": product_version,
                            "architecture": self._get_architecture(file_name)
                        })

                        time.sleep(4)
                    driver.close()
                
                # 다시 main window로 전환 (카탈로그 창)
                driver.switch_to.window(main_window)
                
                # 다운로드 완료 대기 
                self._wait_til_download_ended()

            except Exception as e:
                print(f"\"{link}\"를 처리하던 중 에러가 발생했습니다.")
                print(e)

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
        self._wait_til_download_ended()
        print("\n[INFO] .msu 파일명에서 해시값 제거")

        for file in os.listdir(self._patch_file_path):
            renamed = self._msu_file_name_change(file)

            if file != renamed:
                try:
                    os.rename(self._patch_file_path / file, self._patch_file_path / renamed)
                    print(f"\t{file} -> {renamed}")

                except FileExistsError as fe:
                    print("\n[INFO] 중복된 파일 삭제합니다")
                    print(file)
                    os.remove(self._patch_file_path / file)
                    continue

        return file_dict
    

    # 수집할 OS 대상, QNUMBER, CATALOG URL을 미리 수집해두고 시작
    def _init_patch_data(self) -> None:
        patch_info_dict = self.patch_info_dict
        soup = self.soup
        qnumbers = self.qnumbers

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
        

    def _show_prompt(self) -> None:
        def _remove_patch(removed: str):
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

        patch_info_dict = self.patch_info_dict

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
                _remove_patch(removed.strip())


    def _get_patch_date(self) -> str:
        date_elem = self.soup.find("em").find("strong")
        
        if date_elem == None:
            raise Exception("패치 날짜 정보를 가져올 수 없습니다.")
        
        date = date_elem.text[1:-1].strip().split("/")
        return f"{date[-1]}/{date[0]}/{int(date[1]) + 1}"


    # TODO
    def _get_default_summary(self):
        return "수동 수집이 필요합니다."


    def _get_title_and_summary(self, file_dict) -> dict[str, dict[str, str]]:
        tmp = dict()

        driver = self.driver
        nations = ["en-us", "ko-kr", "ja-jp", "zh-cn"]
        bulletin = "https://support.microsoft.com/{}/help/{}"
        
        for qnumber in file_dict:
            tmp[qnumber] = dict()
            err = False
            
            for nation in nations:
                if err:
                    print(f"[WARN] {qnumber}에 대한 Title, Summary 정보 수집 실패")
                    continue

                try:
                    bulletin_url = bulletin.format(nation, qnumber)
                    driver.get(bulletin_url)

                    self._driver_wait(By.ID, "page-header")
                    self._driver_wait(By.ID, "bkmk_summary")
                    time.sleep(1)

                    soup = BeautifulSoup(driver.page_source, "html.parser")
                    title: str = soup.find(name = "h1", attrs = {"id": "page-header"}).text.strip()
                    section = soup.find(name = "section", attrs = {"id": "bkmk_summary"})   # 없는 경우도 존재
                    ps: ResultSet[BeautifulSoup] = section.find_all(name = "p")
            
                    summary = ""
                    for p in ps:
                        pstrip: str = p.text.strip()
                        if pstrip.startswith("CVE"):
                            summary += pstrip.replace(u"\u2013", "-")
                    
                    tmp[qnumber][nation] = dict()
                    tmp[qnumber][nation]["bulletin_url"] = bulletin_url 
                    tmp[qnumber][nation]["title"] = title
                    tmp[qnumber][nation]["summary"] = summary

                except Exception as _:
                    print(f"[WARN] {qnumber}에 대한 summary를 가져오지 못했습니다.")
                    err = True
                    tmp[qnumber][nation]["summary"] = self._get_default_summary()

                finally:
                    if not err:
                        print(bulletin_url)
                        print(title)
                        print(summary)

        return tmp


    def _check_msu_and_cab_file_exists(self):
        # cab 파일과 msu 파일이 모두 있는지 검사
        for file in os.listdir(self._patch_file_path):
            
            if not file.endswith(".msu"):
                continue

            splt = file.split("-")

            tmp = "-".join([splt[1], splt[2], splt[3]]).replace(".msu", "")
            flag = False

            print(f"{tmp} -> ", end="")

            for cab in os.listdir(self._cab_file_path):
                if tmp in cab:
                    print(f"{cab} 확인", end="")
                    flag = True
                    break
           
            if not flag:
                raise Exception(f"{tmp}에 대한 cab 파일이 확인되지 않습니다.")
            
            print()


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

    
    def _get_common_info(self, cve_string: str, patch_date: str) -> dict[str, dict[str, str]]:
        tmp = dict()

        for qnumber in self.qnumbers:
            tmp[qnumber] = {
                "KBNumber": f"KB{qnumber}",
                "BulletinID": f"MS-KB{qnumber}",
                "cve": cve_string,
                "PatchData": patch_date
            }
        
        return tmp


    def _del_driver(self):
        try:
            del self.qnumbers
            del self.patch_info_dict
            del self.error_patch_dict
            del self.driver

        except Exception as _:
            pass

        finally:
            super()._del_driver()


    def run(self) -> None:
        try:
            # 패치 대상 데이터 초기화
            self._init_patch_data()
            
            # 프롬프트 출력, 패치 대상 데이터 최종 결정(제거)
            self._show_prompt()
            
            # 프롬프트 창 clear
            os.system("cls")

            # 패치 날짜 정보 가져오기 (TODO 문서마다 다름)
            print("------------------------------------------")
            patch_date = datetime.today().strftime("%Y/%m/%d") # self._get_patch_date()
            print("[Patch Date]", patch_date)

            # 패치 CVE 문자열 가져오기
            # 이 이후로 soup 객체를 사용하지 않으므로 메모리 해제
            cve_string = self._get_cve_string()
            print("[CVE List]", cve_string)
            del self.soup
            print("------------------------------------------\n\n")

            # BulletinID, KBNumber, PatchDate, CVE, 중요도 정보 가져오기
            # TODO 중요도 정보 가져오기 (MSRC)s
            common_dict = self._get_common_info(patch_date, cve_string)
            print("[Common Info]")

            for qnumber in common_dict:
                print(f"[{qnumber}]")

                for key, val in common_dict[qnumber].items():
                    print(f"\t- {key}: {val}")
                
                print()

            # 패치 대상의 각 카탈로그 링크에서 패치 파일 다운로드
            # 각 패치 파일 이름과 vendor URL에 대한 Dict 반환
            file_dict = self._download_patch_file(common_dict)
            self._wait_til_download_ended()
            time.sleep(3)

            # msu 파일 압축 해제, WSUSSCAN 파일명 변경 작업, file_dict 업데이트
            self._extract_file_info(file_dict)

            # 각 언어별 bulletin URL에서 제목과 요약 수집
            title_and_summary = self._get_title_and_summary(file_dict)

            # 모든 파일이 정상적으로 존재하는지 검증
            self._check_msu_and_cab_file_exists()

            # 모든 QNumber에 대해 수집되었는지 검증
            self._check_all_qnumber_file_exists()

            # 검증 이후에 공통 정보도 저장 
            self._save_result(self._data_file_path / "common_info.json", common_dict)
            
            # 검증이 끝났으면 결과 json 파일로 저장
            print("\n[INFO] 패치 파일 다운로드 작업 완료")
            self._save_result(self._data_file_path / "patch_file_info.json", file_dict)

            # 각 언어별 title, summary 수집 결과 json 파일로 저장
            self._save_result(self._data_file_path / "title_summary.json", title_and_summary)

            os.system("cls")
            print("[INFO] 프로그램이 정상적으로 종료되었습니다")
        
        except Exception as e:
            print("------------------------------------------------------------")
            print(e)
            print("----------------------- [ 에러 보고 ] -----------------------")
            for qnumber in self.error_patch_dict:
                print(f"[{qnumber}]")
                for err_obj in self.error_patch_dict[qnumber]:
                    for key, val in err_obj.items():
                        print(f"\t{key}: {val}")
                print()
            print("------------------------------------------------------------")

            res = input("[ERR] 모든 파일을 삭제할까요? (y/n): ")

            if res != 'y':
                return
            
            shutil.rmtree(self._data_file_path)
            shutil.rmtree(self._patch_file_path)
            print(e)

        finally:
            # 메모리 해제
            self._del_driver()


if __name__ == "__main__":
    dcm = DotnetCrawlingManager()
    dcm.run()
    