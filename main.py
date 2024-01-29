import sys
from const import SYS_APPENDED_PATHS, DOTNET, JAVA, ADOBE


def run() -> None:
    for path in SYS_APPENDED_PATHS:
        abs_path = r"{}".format(path.absolute())
        sys.path.append(abs_path)
    
    print("어떤 파트를 수집하시나요?")
    category = input(f"1. {DOTNET}, 2. {JAVA}, 3. {ADOBE} ")
    funcs = {DOTNET: run_dotnet, JAVA: run_java, ADOBE: run_adobe}
    funcs[category]()


def run_dotnet():
    from src.validator.dotnet_validator import DotnetValidatorManager
    from src.crawler.dotnet_crawling_manager import DotnetCrawlingManager
    from src.register.dotnet_excel_manager import DotnetExcelManager
    
    dvm = DotnetValidatorManager()
    dcm = DotnetCrawlingManager()
    dem = DotnetExcelManager()
    

def run_java():
    pass


def run_adobe():
    pass


if __name__ == "__main__":
    run()