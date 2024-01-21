import sys
import os

sys.path.append(os.path.abspath(".\\crawling"))
sys.path.append(os.path.abspath(".\\excel_auto"))
sys.path.append(os.path.abspath(".\\hash"))

from crawling.dotnet_crawling_manager import DotnetCrawlingManager
from excel_auto.dotnet_excel_manager import DotnetExcelManager
from hash.dotnet_hash_manager import DotnetHashManager


class DotnetCollector:

    def __init__(self):
        crawler = DotnetCrawlingManager()
        pass


if __name__ == "__main__":
    dc = DotnetCollector()