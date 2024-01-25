from crawler.dotnet_crawling_manager import DotnetCrawlingManager
from crawler.crawling_manager import CrawlingManager
import yaml
import os


if __name__ == "__main__":
    dcm = DotnetCrawlingManager()
    dcm.run()
