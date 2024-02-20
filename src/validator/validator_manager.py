from logger import Logger
from const import AppMeta, ErrorFormat


class ValidatorManager:
    # 프로그램을 시작하기 전 필수 파일들이 모두 존재하는지 검사
    # - meta.yaml, mapper.yaml, patch.xlsx, chromedriver.exe
    def __init__(self):
        """
        Top object of validator.
        This __init__ function executes validating process for all files required  
        """
        self.logger = Logger.get_logger()
        self.logger.info(f"필수 파일 목록 검사")
        
        for path in AppMeta.get_required_file_path():
            if not path.exists():
                err = ErrorFormat.ERR_STR_FORMAT.format(str(path))
                self.logger.critical(f"{err}")
                raise Exception(err)
            self.logger.info(f"{path.name} OK")
            
        self.logger.info(f"필요한 파일 목록이 모두 확인되었습니다.")    
