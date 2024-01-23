import os
import json
import time
import sys
import yaml
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

        # yaml 파일 읽기
        pdir = Path(__file__).parent
        meta_path = pdir / ".." / "bin" / "metadata" / "meta.yaml"

        with open(meta_path, "r", encoding="utf8") as fp:
            self.meta = yaml.load(fp, Loader = yaml.FullLoader)

        self._path = self.meta['path']
        self._bin_path = pdir / Path(self._path['bin'])
        self._chrome_driver_path = pdir / Path(self._path['driver'])
        self._patch_file_path = pdir / Path(self._path['patchfile'])
        self._data_file_path = pdir / Path(self._path['data'])

        # ./bin/patchfiles 폴더가 없으면 생성
        if not self._patch_file_path.exists():
            self._patch_file_path.mkdir()
            (self._patch_file_path / "adobe").mkdir()
            (self._patch_file_path / "java").mkdir()
            (self._patch_file_path / "dotnet").mkdir()

        # ./bin/data 폴더가 없으면 생성
        if not self._data_file_path.exists():
            self._data_file_path.mkdir()

        # ./bin/patchfiles 폴더 비어있는지 검사 
        while True:
            cnt = 0

            for f in self._patch_file_path.iterdir():
                if f.is_file():
                    cnt += 1

            if cnt == 0:
                break

            input(f"{self._patch_file_path.absolute()} 폴더 내 모든 파일을 비우고 <Enter>를 입력하세요.")

        # .NET Blog URL 입력받고 시작
        url = input("크롤링할 .NET 패치노트 주소를 입력해주세요: ")

        # 다운로드 경로 설정
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        options.add_experimental_option("prefs", {
            "download.default_directory": str(self._patch_file_path)
        })
        
        # selenium 버전 높은 경우 -> executable_path Deprecated -> Service 객체 사용
        print(f"Python {sys.version} running")
        try:
            self.driver = webdriver.Chrome(options = options, service = Service(executable_path = self._chrome_driver_path))
        except Exception as _:
            print("[INFO] 구버전 webdriver로 동작합니다.")
            self.driver = webdriver.Chrome(executable_path = str(self._chrome_driver_path), options = options)
        
        # Get 요청 후 HTML 파싱
        self.driver.get(url)
        self._load_all_page()
        self.soup = BeautifulSoup(self.driver.page_source, "html.parser")
        
        print("HTML parsing OK")


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

            time.sleep(1)

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
        time.sleep(1)


    def _driver_wait(self, by: By, name: str):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by, name)),
                f"[ERR] Can't Find {by}, {name}"            
            )

            time.sleep(1)

        except Exception as e:
            print(e)


    def _del_driver(self):
        try:
            del self.soup
            del self.driver
        
        except Exception as _:
            pass


if __name__ == "__main__":
    cm = CrawlingManager()
