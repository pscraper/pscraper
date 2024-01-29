import logging
import sys
from pathlib import Path


# Type
ENC_TYPE = "utf8"


# Folder Path
BIN_PATH = Path.cwd() / "bin"                      
SETTINGS_PATH = BIN_PATH / "settings"
EXE_PATH = BIN_PATH / "exe"
DATA_PATH = BIN_PATH / "data"
PATCH_FILE_PATH = BIN_PATH / "patchfiles"
DOTNET_FILE_PATH = PATCH_FILE_PATH / "dotnet"
DOTNET_CAB_PATH = DOTNET_FILE_PATH / "cabs"


# Src Path
CWD = Path.cwd()
SRC_PATH = CWD / "src"
CRAWLER_PATH = SRC_PATH / "crawler"
REGISTER_PATH = SRC_PATH / "register"
VALIDATOR_PATH = SRC_PATH / "validator"
SYS_APPENDED_PATHS = [CWD, SRC_PATH, CRAWLER_PATH, REGISTER_PATH, VALIDATOR_PATH]


# File Path
META_FILE_PATH = SETTINGS_PATH / "meta.yaml"        # 프로그램에서 사용되는 메타 정보를 한 곳에서 관리하기 위한 파일
MAPPER_FILE_PATH = SETTINGS_PATH / "mapper.yaml"    # 엑셀 파일의 제목과 실제 버전의 키를 매핑해주기 위한 파일
EXCEL_FILE_PATH = EXE_PATH / "patch.xlsx"           # 원본 엑셀 파일 (복사해서 사용)
CHROME_DRIVER_PATH = EXE_PATH / "chromedriver.exe"  # 크롤링을 위한 크롬드라이버 파일
RESULT_FILE_PATH = DATA_PATH / "result.json"        # 수집 결과를 저장하는 파일 (크롤링 이후 생성)
LOG_FILE_PATH = BIN_PATH / "log.txt"                # 프로그램 실행 중 로깅을 위한 파일


# 프로그램 시작 전 필수 파일 리스트
REQUIRED_BEFORE_STARTED = [META_FILE_PATH, MAPPER_FILE_PATH, EXCEL_FILE_PATH, RESULT_FILE_PATH]


# Format
err_format = "[ERR] Can't Find {}"


# Logging
logger = logging
stdout_handler = logger.StreamHandler(stream = sys.stdout)              # 콘솔 출력을 위한 핸들러
file_handler = logger.FileHandler(LOG_FILE_PATH, encoding = "utf8")     # 파일 출력을 위한 핸들러
logger.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s %(levelname)s: %(message)s',
    datefmt = '[%m/%d/%Y %I:%M:%S] %p',
    handlers = [stdout_handler, file_handler]
)