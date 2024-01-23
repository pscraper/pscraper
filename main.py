from crawler.dotnet_crawling_manager import DotnetCrawlingManager
from crawler.crawling_manager import CrawlingManager
import yaml
import os


meta_path = r"C:\Users\seungsu\Desktop\projects\pscraper\bin\metadata\meta.yaml"

if __name__ == "__main__":
    dcm = DotnetCrawlingManager()
    dcm.run()
