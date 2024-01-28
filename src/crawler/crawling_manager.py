import os
import json
import time
import sys
import yaml
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from pathlib import Path


class CrawlingManager:
    def __init__(self):
        os.system("cls")

        # init 파일 경로 설정
        bin = Path.cwd() / "bin"
        meta = bin / "settings" / "meta.yaml"

        logging.basicConfig(
            filename = bin / "log.txt", 
            level = logging.INFO,
            format = r'%(asctime)s %(levelname)s:%(message)s',
            datefmt = r'[%m/%d/%Y %I:%M:%S] %p'
        )

        self.logger = logging

        # settings 경로 체크
        if not os.path.exists(meta):
            logging.warn("meta.yaml 파일을 읽어들일 수 없습니다.")
            return

        # 파일 읽어서 meta 객체 초기화
        with open(meta, "r", encoding="utf8") as fp:
            self.meta = yaml.load(fp, Loader = yaml.FullLoader)

        self._path = self.meta['path']
        self._chrome_driver_path = bin / Path(self._path['driver'])
        self._data_file_path = bin / Path(self._path['data'])
        self._patch_file_path = bin / "patchfiles" 

        if not self._patch_file_path.exists():
            self._patch_file_path.mkdir()

        if "java" not in os.listdir(self._patch_file_path):
            os.mkdir(self._patch_file_path / "java")

        if "adobe" not in os.listdir(self._patch_file_path):
            os.mkdir(self._patch_file_path / "adobe")

        if "dotnet" not in os.listdir(self._patch_file_path):
            os.mkdir(self._patch_file_path / "dotnet")

        if not self._data_file_path.exists():
            self._data_file_path.mkdir()       

        patch_name = input("어떤 패치를 수집하시나요? (java/adobe/dotnet) ")
        url = input("크롤링할 패치노트 주소를 입력해주세요: ")

        # 다운로드 경로 설정
        options = webdriver.ChromeOptions()

        for option in self.meta['driver_options']:
            print(f"Chrome Option {option} Added.")
            options.add_argument(option)

        options.add_experimental_option("prefs", {
            "download.default_directory": str(self._patch_file_path / patch_name)
        })

        # selenium 버전 높은 경우 -> executable_path Deprecated -> Service 객체 사용
        logging.info(f"Python {sys.version} running")

        try:
            self.driver = webdriver.Chrome(options = options, service = Service(executable_path = self._chrome_driver_path))

        except Exception as _:
            logging.info("[INFO] 구버전 Selenium으로 동작합니다.")
            self.driver = webdriver.Chrome(executable_path = str(self._chrome_driver_path), options = options)
        
        # Get 요청 후 HTML 파싱
        self.driver.get(url)
        self._load_all_page()
        self.soup = BeautifulSoup(self.driver.page_source, "html.parser")
        
        logging.info("HTML parsing OK")


    # patchfiles 폴더에 중복된 파일이 있는지 검사
    def _is_already_exists(self, name) -> bool:
        for file in self._patch_file_path.iterdir():
            if file.name.startswith(name):
                return True
        
        return False


    def _wait_til_download_ended(self):
        while True: 
            dl = False
            for file in self._patch_file_path.iterdir():
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
            logging.warn(e)


    def _del_driver(self):
        try:
            del self.soup
            del self.driver
            del self.meta
        
        except Exception as _:
            pass

    
    def _error_report(self, e: Exception, error_patch_dict: dict[str, list[dict[str, str]]]):
        for qnumber in error_patch_dict:
            self.logger.warning(f"[{qnumber}]")
            self.logger.warning(e)

            for err_obj in error_patch_dict[qnumber]:
                for key, val in err_obj.items():
                    self.logger.warning(f"\t{key}: {val}")


if __name__ == "__main__":
    cm = CrawlingManager()
