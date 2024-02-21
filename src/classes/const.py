from pathlib import Path


# APP META
class AppMeta:
    APP_NAME = "pscraper"
    ENC_TYPE = "utf8"
    REPORT_SERVER_URL = "http://localhost:8000"
    
    # 프로그램 시작 전 모듈 import를 위한 경로 리스트
    @staticmethod
    def get_required_file_path():
        return [FilePath.META, FilePath.EXCEL, FilePath.CHROME_DRIVER]

    # 각 모듈의 루트 경로 모음 (sys 경로에 등록)
    @staticmethod
    def get_sys_appended_path():
        return [SrcPath.CRAWLER, SrcPath.REGISTER, SrcPath.VALIDATOR, SrcPath.UTILS, SrcPath.FILE_HANDLER]

    # 대체해야 하는 특정 유니코드 모음 리스트
    @staticmethod
    def get_replaced_unicodes():
        return [{u'\u2013': ' - '}, {u'\u00a0': ''}, {u'\n': ''}] 


# Category
class Category:
    DOTNET = "Dotnet"
    JAVA = "Java"
    ADOBE = "Adobe"


# 파일 다운로드 상태
class FileStatus:
    DOWNLOADING = "crdownload"
    TMP = "tmp"


# SLEEP
class Sleep:
    LONG = 3
    MEDIUM = 2
    SHORT = 1


# ADOBE DOM STRINGS
class AdobeDOM:
    SECURITY_BULLETIN = "//*[@id=\"security-bulletin\"]"
    OPTIONAL_TITLE = "//*[@id=\"planned-update-feb-13-2024\"]/p"
    CLASSIC_UL = "//*[@id=\"classic-track-installers\"]/ul"
    CLASSIC_INSTALL_A = "//*[@id=\"id1\"]/tbody/tr[1]/td[3]/p/a"
    CONTINUOUS_UL = "//*[@id=\"continuous-track-installers\"]/ul"


# Folder Path
class DirPath:
    BIN = Path.cwd().parent / "bin"                      
    SETTINGS = BIN / "settings"
    EXE = BIN / "exe"
    DATA = BIN / "data"
    PATCH = BIN / "patchfiles"
    LOG = BIN / "logs"
    DOTNET = PATCH / "dotnet"
    CAB = DOTNET / "cabs"
    ADOBE = PATCH / "adobe"


# File Path
class FilePath:
    META = DirPath.SETTINGS / "meta.yaml"     
    EXCEL = DirPath.EXE / "patch.xlsx"        
    CHROME_DRIVER = DirPath.EXE / "chromedriver.exe"
    RESULT = DirPath.DATA / "result.json"
    MAPPER = DirPath.DATA / "mapper.txt"
    LOG = DirPath.LOG / "log.txt"


# Src Path
class SrcPath:
    CWD = Path.cwd().parent
    SRC = CWD / "src"
    CRAWLER = SRC / "crawler"
    REGISTER = SRC / "register"
    VALIDATOR = SRC / "validator"
    FUNCS = SRC / "funcs"
    UTILS = SRC / "utils"
    FILE_HANDLER = SRC / "filehandler"


# 에러 포멧 
class ErrFormat:
    _CANT_FIND = "[ERR] CAN'T FIND OBJECT {}"
    _CANT_EXTRACT = "[ERR] CAN'T EXTRACT ARCHITECTURE FROM FILENAME {}"

    @classmethod
    def cant_find_obj(cls, obj: str) -> str:
        return cls._CANT_FIND.format(obj)
    
    @classmethod
    def cant_extract(cls, filename: str) -> str:
        return cls._CANT_EXTRACT.format(filename)
