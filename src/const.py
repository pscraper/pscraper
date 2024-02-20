from pathlib import Path


# APP META
class AppMeta:
    APP_NAME = "pscraper"
    ENC_TYPE = "utf8"
    REPORT_SERVER_URL = "http://localhost:8000"
    
    # 프로그램 시작 전 모듈 import를 위한 경로 리스트
    @staticmethod
    def get_required_file_path():
        return [FilePath.META_FILE_PATH, FilePath.EXCEL_FILE_PATH, FilePath.CHROME_DRIVER_PATH]

    # 각 모듈의 루트 경로 모음 (sys 경로에 등록)
    @staticmethod
    def get_sys_appended_path():
        return [SrcPath.CRAWLER_PATH, SrcPath.REGISTER_PATH, SrcPath.VALIDATOR_PATH, SrcPath.UTILS_PATH, SrcPath.FILE_HANDLER_PATH]

    # 대체해야 하는 특정 유니코드 모음 리스트
    @staticmethod
    def get_replaced_unicodes():
        return [{u'\u2013': ' - '}, {u'\u00a0': ''}, {u'\n': ''}] 


# SLEEP
class Sleep:
    LONG = 3
    MEDIUM = 2
    SHORT = 1


# DOTNET DOM STRINGS
class DotnetDOM:
    CVE_STR = r"CVE-\d+-\d+"
    CVE_ID = r"^cve"
    KB_STR = r"^KB\\d{7}"
    PF_DOWNLOAD = "//*[@id=\"downloadFiles\"]"
    TS_HEADER = "page-header"      # Title_and_Summary Header ID
    TS_SUMMARY = "bkmk_summary"    # Title_and_Summary Summary ID


# ADOBE DOM STRINGS
class AdobeDOM:
    ADB_SECURITY_BULLETIN = "//*[@id=\"security-bulletin\"]"
    ADB_OPTIONAL_TITLE = "//*[@id=\"planned-update-feb-13-2024\"]/p"
    ADB_CLASSIC_UL = "//*[@id=\"classic-track-installers\"]/ul"
    ADB_CLASSIC_INSTALL_A = "//*[@id=\"id1\"]/tbody/tr[1]/td[3]/p/a"
    ADB_CONTINUOUS_UL = "//*[@id=\"continuous-track-installers\"]/ul"


# Folder Path
class DirPath:
    BIN_PATH = Path.cwd().parent / "bin"                      
    SETTINGS_PATH = BIN_PATH / "settings"
    EXE_PATH = BIN_PATH / "exe"
    DATA_PATH = BIN_PATH / "data"
    PATCH_DIR_PATH = BIN_PATH / "patchfiles"
    DOTNET_DIR_PATH = PATCH_DIR_PATH / "dotnet"
    CAB_DIR_PATH = DOTNET_DIR_PATH / "cabs"
    ADOBE_DIR_PATH = PATCH_DIR_PATH / "adobe"


# File Path
class FilePath:
    META_FILE_PATH = DirPath.SETTINGS_PATH / "meta.yaml"     
    EXCEL_FILE_PATH = DirPath.EXE_PATH / "patch.xlsx"        
    CHROME_DRIVER_PATH = DirPath.EXE_PATH / "chromedriver.exe"
    RESULT_FILE_PATH = DirPath.DATA_PATH / "result.json"
    MAPPER_FILE_PATH = DirPath.DATA_PATH / "mapper.txt"


# Src Path
class SrcPath:
    CWD = Path.cwd().parent
    SRC_PATH = CWD / "src"
    CRAWLER_PATH = SRC_PATH / "crawler"
    REGISTER_PATH = SRC_PATH / "register"
    VALIDATOR_PATH = SRC_PATH / "validator"
    FUNCS_PATH = SRC_PATH / "funcs"
    UTILS_PATH = SRC_PATH / "utils"
    FILE_HANDLER_PATH = SRC_PATH / "filehandler"


# 에러 포멧 
class ErrorFormat:
    ERR_STR_FORMAT = "[ERR] CAN'T FIND OBJECT {}"
    ERR_ARCH_FORMAT = "[ERR] CAN'T EXTRACT ARCHITECTURE FROM FILENAME {}"


