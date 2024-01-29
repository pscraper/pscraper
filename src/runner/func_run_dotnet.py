

def run_dotnet(url: str):
    from validator.dotnet_validator import DotnetValidatorManager
    from crawler.dotnet_crawling_manager import DotnetCrawlingManager
    from register.dotnet_excel_manager import DotnetExcelManager
    
    dvm = DotnetValidatorManager()
    dcm = DotnetCrawlingManager(url)
    dem = DotnetExcelManager()