import os
import json
import time
import sys
import yaml
import shutil
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from const import (
    META_FILE_PATH,
    PATCH_FILE_PATH,
    DATA_PATH,
    CHROME_DRIVER_PATH,
    ENC_TYPE,
    logger
)


class CrawlingManager:
    def __init__(self, category: str, url: str):
        """
        Top object of crawler. 
        This __init__ function contains initializing Chrome Webdriver, parsing HTML from received URL, 
        making absent directories.

        Args:
            category(str) : Enum value of Adobe / Java / .Net (defined classes.py)
            url(str) : Base URL for crawling
        """
        # 파일 읽어서 meta 객체 초기화
        with open(META_FILE_PATH, "r", encoding = ENC_TYPE) as fp:
            self.meta = yaml.load(fp, Loader = yaml.FullLoader)

        # bin\patchfiles 폴더 생성
        if not PATCH_FILE_PATH.exists():
            logger.info(f"Make Dir: {PATCH_FILE_PATH}")
            os.mkdir(PATCH_FILE_PATH)

        # bin\data 폴더 생성
        if not DATA_PATH.exists():
            logger.info(f"Make Dir: {DATA_PATH}")
            os.mkdir(DATA_PATH)

        # bin\patchfiles\{type} 폴더 생성
        # 기존에 존재하면 삭제
        SUB_DIR = PATCH_FILE_PATH / category.lower()
        if os.path.exists(SUB_DIR):
            logger.warning(f"Remove Dir Tree: {SUB_DIR}")
            shutil.rmtree(SUB_DIR)
        
        SUB_DIR.mkdir()
        logger.info(f"Make Dir: {SUB_DIR}")

        # 다운로드 경로 설정
        options = webdriver.ChromeOptions()

        for option in self.meta['driver_options']:
            logger.info(f"Chrome Option {option} Added.")
            options.add_argument(option)

        options.add_experimental_option("prefs", {
            "download.default_directory": str(SUB_DIR)
        })

        # selenium 버전 높은 경우 -> executable_path Deprecated -> Service 객체 사용
        try:
            self.driver = webdriver.Chrome(options = options, service = Service(executable_path = str(CHROME_DRIVER_PATH)))

        except Exception as _:
            logger.info(f"구버전 ChromeDriver 객체로 동작합니다.")
            self.driver = webdriver.Chrome(executable_path = str(CHROME_DRIVER_PATH), options = options)
        
        # Get 요청 후 HTML 파싱
        self.driver.get(url)
        self._load_all_page()
        self.soup = BeautifulSoup(self.driver.page_source, "html.parser")
        
        # Logging
        logger.info(f"Successfully initlaize")
        logger.info(f"Base URL: {url}")
        logger.info(f"Category: {category}")
        logger.info(f"Python Version: {sys.version}")
        logger.info(f"HTML parsing OK")


    # patchfiles 폴더에 중복된 파일이 있는지 검사
    def _is_already_exists(self, name) -> bool:
        for file in PATCH_FILE_PATH.iterdir():
            if file.name.startswith(name):
                return True
        
        return False


    def _wait_til_download_ended(self):
        while True: 
            dl = False
            for file in PATCH_FILE_PATH.iterdir():
                if file.name.endswith("crdownload"):
                    dl = True

            time.sleep(0.5)

            if not dl:
                break


    def _save_result(self, file_name: str, result_dict: dict):
        with open(file_name, "w", encoding = "utf8") as fp:
            json.dump(
                obj = result_dict, 
                fp = fp, 
                indent = 4,
                sort_keys = True, 
                ensure_ascii = False
            )


    # 동적 페이지의 경우 로딩을 위해 전체 페이지 탐색 
    def _load_all_page(self):
        chains = ActionChains(self.driver)

        for _ in range(10):
            chains.send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(0.5)

        chains.send_keys(Keys.HOME).perform()


    def _driver_wait(self, by: By, name: str):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by, name)),
                f"[ERR] Can't Find {by}, {name}"            
            )

            time.sleep(1)

        except Exception as e:
            logger.warn(e)


    def _del_driver(self):
        try:
            del self.soup
            del self.driver
            del self.meta
        
        except Exception as _:
            pass

    
    def _error_report(self, e: Exception, error_patch_dict: dict[str, list[dict[str, str]]]):
        for qnumber in error_patch_dict:
            logger.warning(f"[{qnumber}]")
            logger.warning(e)

            for err_obj in error_patch_dict[qnumber]:
                for key, val in err_obj.items():
                    logger.warning(f"\t{key}: {val}")


if __name__ == "__main__":
    test = CrawlingManager("dotnet", "http://www.naver.com")