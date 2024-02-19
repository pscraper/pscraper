import time
from typing import Any
from selenium.webdriver.common.by import By
from crawler.adobe_crawling_manager import AdobeCrawlingManager
from classes import AdobeCommon, AdobeContinuous
from const import (
    ADB_SECURITY_BULLETIN,
    ADOBE_FILE_PATH,
    ADB_PATCH_NOTE_URL, 
    ADB_CONTINUOUS_UL, 
    ADB_CONTINUOUS_INSTALL_A_X32,
    ADB_CONTINUOUS_INSTALL_A_X64,
    SLEEP_SHORT,
    logger
)


class AdobeContinuousCrawlingManager(AdobeCrawlingManager):
    def __init__(self, category: str):
        super().__init__(category, ADB_PATCH_NOTE_URL)
    
    
    def run(self):
        logger.info(f"[Adobe Continuous Track] 전체 패치 목록 리스트")
        link = self.get_patch_link(ADB_CONTINUOUS_UL)
        
        logger.info(f"전체 패치파일을 다운로드합니다..")
        file_names = self.download_patch_files(link)
        for file_name in file_names:
            logger.info(f"- Download: {file_name}")
        
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
        self.driver.get(link)
        self._load_all_page()
        file_names = list()
        
        for inst in [ADB_CONTINUOUS_INSTALL_A_X32, ADB_CONTINUOUS_INSTALL_A_X64]:
            self._driver_wait(by = By.XPATH, name = inst)
            trs = self.driver.find_elements(by = By.TAG_NAME, value = "tr")
            
            for tr in trs:
                tds = tr.find_elements(by = By.TAG_NAME, value = "td")
                
                for td in tds:
                    try:
                        a = td.find_element(by = By.TAG_NAME, value = "a")
                        if self._is_already_exists(ADOBE_FILE_PATH, a.text):
                            continue
                        
                        file_names.append(a.text)
                        a.click()
                        time.sleep(SLEEP_SHORT)
                    
                    except Exception as _:
                        logger.info(td.text)
                        continue
        
        self._wait_(self.CRDOWNLOAD)
        self._wait_(self.TMP)
        
        return file_names