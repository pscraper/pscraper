from const import REQUIRED_BEFORE_STARTED, logger, err_format


class ValidatorManager:
    # 프로그램을 시작하기 전 필수 파일들이 모두 존재하는지 검사
    # - meta.yaml, mapper.yaml, patch.xlsx, chromedriver.exe
    def __init__(self):
        """
        Top object of validator.
        This __init__ function executes validating process for all files required  
        """

        name = __class__.__name__
        logger.info(f"[{name}] 파일 목록 검사")
        
        for path in REQUIRED_BEFORE_STARTED:
            if not path.exists():
                err = err_format.format(str(path))
                logger.critical(f"[{name}] err")
                raise Exception(err)
            
            logger.info(f"[{name}] - {path.name} OK")
            
        logger.info(f"[{name}] 필요한 파일 목록이 모두 확인되었습니다.")    
