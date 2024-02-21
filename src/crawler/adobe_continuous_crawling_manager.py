import time
from selenium.webdriver.common.by import By
from crawler.adobe_crawling_manager import AdobeCrawlingManager
from utils.util_func_json import save_json_result


class AdobeContinuousCrawlingManager(AdobeCrawlingManager):
    def __init__(self, category: str):
        super().__init__(category, ADB_PATCH_NOTE_URL)
    
    
    def run(self):
        self.logger.info(f"[Adobe Continuous Track] 전체 패치 목록 리스트")
        link = self.get_patch_link(ADB_CONTINUOUS_UL)
        
        self.logger.info(f"전체 패치파일을 다운로드합니다..")
        file_names = self.download_patch_files(link)
        self.update_file_names(file_names)
        
        # 패치 버전 (2300820533)
        version = self.extract_version_from_file_name(file_names[0])
        
        # summary
        summary = self.get_summary()
        
        # 보안 패치인 경우 보안 업데이트 노트에 들어가서 추가 정보를 가져온다 
        if self.is_security_update():
            path = ADB_SECURITY_BULLETIN + "/p"
            p = self.driver.find_element(by = By.XPATH, value = path)
            a_elems = p.find_elements(by = By.TAG_NAME, value = "a")
            
            for a_elem in a_elems:
                
                
                if a_elem.text.strip() == AdobeCommon.READER:
                    version_with_dot = self.version_with_dot(version)
                    title = self.get_security_title(AdobeCommon.READER, version_with_dot)
                    
                elif a_elem.text.strip() == AdobeCommon.READER:
                    pass
                    
    
    def download_patch_files(self, link: str) -> list[str]:
        file_names = list()
        self.driver.get(link)
        self._load_all_page()
        
        args = {"by": By.ID, "value": "available-installers", "element": self.driver}
        container = self._driver_wait_and_find(**args)
        
        for div in container.find_elements(by = By.CLASS_NAME, value = "wy-table-responsive"):
            table = div.find_element(by = By.TAG_NAME, value = "table")
            title = table.find_element(by = By.TAG_NAME, value = "span").text
            if not title.startswith("Windows"):
                continue

            self.logger.info(f"{title} 다운로드 작업 중..")
            trs = table.find_element(by = By.TAG_NAME, value = "tbody").find_elements(by = By.TAG_NAME, value = "tr")
            
            for tr in trs:
                td = tr.find_elements(by = By.TAG_NAME, value = "td")[2]
                
                try:
                    a = td.find_element(by = By.TAG_NAME, value = "a")
                    if self._is_already_exists(ADOBE_FILE_PATH, a.text):
                        continue
                        
                    file_names.append(a.text)
                    a.click()
                    self.logger.info(f"- {a.text}")
                    time.sleep(SLEEP_LONG)
                    
                except Exception as _:
                    continue
        
        self._wait_(ADOBE_FILE_PATH, self.CRDOWNLOAD)
        self._wait_(ADOBE_FILE_PATH, self.TMP) 
        
        return file_names
    
    
    def update_file_names(self, file_names: list[str]) -> None:
        keys = list(AdobeContinuous.FK_MAPPER.keys())
        
        for file_name in file_names:
            for key in keys:
                if file_name.startswith(key):
                    val = AdobeContinuous.FK_MAPPER[key]
                    if "files" not in self.result[val]:
                        self.result[val]["files"] = list()
                    self.result[val]["files"].append(file_name)
                    break
        
        save_json_result(RESULT_FILE_PATH, self.result)