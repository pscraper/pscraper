from crawler.adobe_classic_crawling_manager import AdobeClassicCrawlingManager
from crawler.adobe_continuous_crawling_manager import AdobeContinuousCrawlingManager
from logger import LogManager


logger = LogManager.get_logger()


def run_adobe(url: str, category: str, phase: int) -> None:
    try:
        if phase == 1:
            _run_adobe_phase1(url, category)
        
    except Exception as e:
        logger.critical(e)
        raise Exception("예상치 못한 에러 발생")
    

def _run_adobe_phase1(url: str, category: str):
    res = int(input("(1) Continuos Track\t(2) Classic Track\n>> "))
    if res not in [1, 2]:
        raise Exception("적절한 항목을 선택해주세요")
    
    crawler = AdobeContinuousCrawlingManager(url, category) if res == 1 else AdobeClassicCrawlingManager(url, category)
    crawler.run()


def _run_adobe_phase2():
    pass