import sys
from classes import Category
from const import logger
from funcs.func_run_adobe import run_adobe
from funcs.func_run_dotnet import run_dotnet, _run_dotnet_after_scraping
from funcs.func_run_java import run_java


# conda activate {env_name}
# python pscraper.py {Category} {url}
def run(category: str, url: str) -> None:    
    DOTNET = Category.DOTNET.name.lower()
    JAVA = Category.JAVA.name.lower()
    ADOBE = Category.ADOBE.name.lower()
    
    if category == DOTNET:
        if sys.argv[2] == "--write-excel":
            _run_dotnet_after_scraping(category)
        
        else:
            run_dotnet(url, DOTNET)
    
    elif category == JAVA:
        run_java(url, JAVA)

    elif category == ADOBE:
        run_adobe(url, ADOBE)

    else:
        raise Exception(f"Unexpected Category name: {category}")


if __name__ == "__main__":
    logger.info(f"{sys.argv[0]} Running")

    # exe 파일을 실행한 경우, 명령행 인자 없이 실행한 경우
    if len(sys.argv) == 1:
        category = input("Category: ")
        patch_note = input("Patch Note URL: ")
        run(category, patch_note)

    # 명령행 인자로 실행한 경우
    else:
        run(sys.argv[1], sys.argv[2])