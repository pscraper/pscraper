import sys
import os
from classes import Category
from const import (
    SYS_APPENDED_PATHS,
    logger
)


def run() -> None:
    os.system("cls")

    print("어떤 파트를 수집하시나요?")
    
    DOTNET = Category.DOTNET.name
    JAVA = Category.JAVA.name
    ADOBE = Category.ADOBE.name

    category = input(f"(1) {DOTNET} \t (2) {JAVA} \t (3) {ADOBE}\n")
    url = input("URL: ")

    funcs = {
        DOTNET: run_dotnet, "1": run_dotnet,
        JAVA: run_java, "2": run_java,
        ADOBE: run_adobe, "3": run_adobe
    }

    funcs[category](url)


def run_dotnet(url: str):
    from validator.dotnet_validator import DotnetValidatorManager
    from crawler.dotnet_crawling_manager import DotnetCrawlingManager
    from register.dotnet_excel_manager import DotnetExcelManager
    
    dvm = DotnetValidatorManager()
    dcm = DotnetCrawlingManager(url)
    dem = DotnetExcelManager()
    

def run_java(url: str):
    pass


def run_adobe(url: str):
    pass


if __name__ == "__main__":
    for path in SYS_APPENDED_PATHS:
        abs_path = r"{}".format(path.absolute())
        logger.info(f"path appended to sys: {abs_path}")
        sys.path.append(abs_path)

    run()