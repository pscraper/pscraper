import os
import time
import sys
import yaml
import shutil
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from logger import LogManager
from classes.const import Sleep, DirPath, FilePath, AppMeta


class CrawlingManager:
    DRIVER_PREFS = {
        "directory_upgrade": True,
        "safebrowsing": {
            "enabled": True,
            "malware": {"enabled": True}
        },
        "alternate_error_pages": True,
        "browser": {
            "safebrowsing": {
                "enabled": True,
                "malware":{"enabled": True}
            }
        }
    }
    
    
    def __init__(self, category: str, url: str):
        """
        Top object of crawler. 
        This __init__ function contains initializing Chrome Webdriver, parsing HTML from received URL, 
        making absent directories.

        Args:
            category(str) : Enum value of Adobe / Java / .Net (defined classes.py)
            url(str) : Base URL for crawling
        """
        self.logger = LogManager.get_logger()

        # 파일 읽어서 meta 객체 초기화
        with open(FilePath.META, "r", encoding = AppMeta.ENC_TYPE) as fp:
            self.meta = yaml.load(fp, Loader = yaml.FullLoader)

        # bin\patchfiles 폴더 생성
        if not DirPath.PATCH.exists():
            self.logger.info(f"Make Dir: {DirPath.PATCH}")
            os.mkdir(DirPath.PATCH)

        # bin\data 폴더 생성
        if not DirPath.DATA.exists():
            self.logger.info(f"Make Dir: {DirPath.DATA}")
            os.mkdir(DirPath.DATA)

        # bin\patchfiles\{type} 폴더 생성
        # 기존에 존재하면 삭제
        category_path = DirPath.PATCH / category
        
        if os.path.exists(category_path):
            self.logger.warning(f"Remove Dir Tree: {category_path}")
            shutil.rmtree(category_path)
        
        category_path.mkdir()
        self.logger.info(f"Make Dir: {category_path}")

        # 다운로드 경로 설정
        self.DRIVER_PREFS.update({"download.default_directory": str(category_path)})
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", self.DRIVER_PREFS)
        for option in self.meta['driver_options']:
            self.logger.info(f"Chrome Option {option} Added.")
            options.add_argument(option)

        # selenium 버전 높은 경우 -> executable_path Deprecated -> Service 객체 사용
        try:
            self.driver = webdriver.Chrome(options = options, service = Service(executable_path = str(FilePath.CHROME_DRIVER)))

        except Exception as _:
            self.logger.info(f"구버전 ChromeDriver 객체로 동작합니다.")
            self.driver = webdriver.Chrome(executable_path = str(FilePath.CHROME_DRIVER), options = options)
        
        # Get 요청 후 HTML 파싱
        self.driver.get(url)
        self._load_all_page()
        self.soup = BeautifulSoup(self.driver.page_source, "html.parser")
        
        # Logging
        self.logger.info(f"Successfully Initialized")
        self.logger.info(f"Python Version: {sys.version}")
        self.logger.info(f"Category: {category}")
        self.logger.info(f"Base URL: {url}")
        self.logger.info(f"HTML parsing OK")


    # patchfiles\dotnet 폴더에 중복된 파일이 있는지 검사
    def _is_already_exists(self, path: Path, name: str) -> bool:
        for file in path.iterdir():
            if file.name.startswith(name):
                return True
        
        return False


    # patchfiles\dotnet 폴더에 다운로드 중인 파일이 있는지 검사
    def _wait_(self, path: Path, ends: str):
        while True: 
            dl = False
            for file in path.iterdir():
                if file.name.endswith(ends):
                    dl = True
                    break

            time.sleep(Sleep.SHORT)
            if not dl:
                break
            

    # 동적 페이지의 경우 로딩을 위해 전체 페이지 탐색 
    def _load_all_page(self):
        chains = ActionChains(self.driver)
        for _ in range(10):
            chains.send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(Sleep.SHORT)

        chains.send_keys(Keys.HOME).perform()


    def _driver_wait_and_find(self, element: WebElement, by: By, value: str) -> WebElement:
        self._driver_wait(by, value)
        return element.find_element(by, value)


    def _driver_wait_and_finds(self, element: WebElement, by: By, value: str) -> list[WebElement]:
        self._driver_wait(by, value)
        return element.find_elements(by, value)


    def _driver_wait(self, by: By, value: str):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by, value)), f"[ERR] Can't Find {by}, {value}"
            )
            time.sleep(Sleep.SHORT)

        except Exception as e:
            self.logger.warn(e)


    def _del_driver(self):
        try:
            del self.soup
            del self.driver
            del self.meta
        
        except Exception as _:
            pass