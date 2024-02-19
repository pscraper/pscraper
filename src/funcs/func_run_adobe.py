from crawler.adobe_classic_crawling_manager import AdobeClassicCrawlingManager
from crawler.adobe_continuous_crawling_manager import AdobeContinuousCrawlingManager


def run_adobe(category: str):
    res = int(input("(1) Continuos Track\t(2) Classic Track\n>> "))
    if res not in [1, 2]:
        raise Exception("적절한 항목을 선택해주세요")
    
    crawler = AdobeContinuousCrawlingManager(category) if res == 1 else AdobeClassicCrawlingManager(category)
    crawler.run()
