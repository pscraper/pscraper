from crawler.adobe_classic_crawling_manager import AdobeClassicCrawlingManager
from crawler.adobe_continuous_crawling_manager import AdobeContinuousCrawlingManager
from const import logger


def run_adobe(url: str, category: str) -> None:
    try:
        _run_adobe(url, category)
        
    except Exception as e:
        logger.critical(e)
        raise Exception("예상치 못한 에러 발생")
    

def _run_adobe(url: str, category: str):
    res = int(input("(1) Continuos Track\t(2) Classic Track\n>> "))
    if res not in [1, 2]:
        raise Exception("적절한 항목을 선택해주세요")
    
    crawler = AdobeContinuousCrawlingManager(url, category) if res == 1 else AdobeClassicCrawlingManager(url, category)
    crawler.run()


def run_adobe_after_scraping():
    pass