from const import REQUIRED_BEFORE_STARTED, logger, ERR_STR_FORMAT 


class ValidatorManager:
    # 프로그램을 시작하기 전 필수 파일들이 모두 존재하는지 검사
    # - meta.yaml, mapper.yaml, patch.xlsx, chromedriver.exe
    def __init__(self):
        """
        Top object of validator.
        This __init__ function executes validating process for all files required  
        """

        logger.info(f"파일 목록 검사")
        
        for path in REQUIRED_BEFORE_STARTED:
            if not path.exists():
                err = ERR_STR_FORMAT.format(str(path))
                logger.critical(f"{err}")
                raise Exception(err)
            
            logger.info(f"{path.name} OK")
            
        logger.info(f"필요한 파일 목록이 모두 확인되었습니다.")    
