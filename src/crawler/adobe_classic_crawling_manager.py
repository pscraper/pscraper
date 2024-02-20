from selenium.webdriver.common.by import By
from crawler.adobe_crawling_manager import AdobeCrawlingManager
from const import ADB_PATCH_NOTE_URL, ADB_CLASSIC_UL, ADB_CLASSIC_INSTALL_A


class AdobeClassicCrawlingManager(AdobeCrawlingManager):
    def __init__(self, category: str):
        super().__init__(category, ADB_PATCH_NOTE_URL)
    
    def run(self):
        # 전체 패치 목록 리스트 조회
        self.logger.info(f"[Adobe Classic Track] 전체 패치 목록 리스트")
        link = self.get_patch_link(ADB_CLASSIC_UL)
        
        # 패치 제목 수집
        # Security Bulletin ID가 있는 경우 패치 제목 뒤 조합
        # title = self.get_patch_title()
        
        # Summary 수집
        # 보안 패치: Security Bulletin 내용 수집
        # 비보안 패치: 패치노트 상단 내용 수집 
        # 둘 다 없는 경우: Adobe has released update for <패치 버전> for Windows. This update address some bug fixes and improvements.
        summary = self.get_summary()
        
        # 패치파일 수집
        file_name = self.download_patch_files(link)[0]
        self.logger.info(f"[Download] {file_name}")
        
    
    def download_patch_files(self, link) -> list[str]:
        self.driver.get(link)
        self._load_all_page()
        self._driver_wait(by = By.XPATH, name = ADB_CLASSIC_INSTALL_A)
        
        install_a_elem = self.driver.find_elements(by = By.XPATH, value = ADB_CLASSIC_INSTALL_A)[0]
        install_a_elem.click()
        self._wait_(self.CRDOWNLOAD)
        self._wait_(self.TMP)
        
        return [install_a_elem.text]
    
    