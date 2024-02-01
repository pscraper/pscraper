import sys
from classes import Category
from const import logger
from funcs.func_run_adobe import run_adobe
from funcs.func_run_dotnet import run_dotnet
from funcs.func_run_java import run_java


# conda activate {env_name}
# python pscraper.py {Category} {url}
def run(category: str, url: str) -> None:    
    DOTNET = Category.DOTNET.name.lower()
    JAVA = Category.JAVA.name.lower()
    ADOBE = Category.ADOBE.name.lower()
    
    if category == DOTNET:
        run_dotnet(url, DOTNET)
    
    elif category == JAVA:
        run_java(url, JAVA)

    elif category == ADOBE:
        run_adobe(url, ADOBE)

    else:
        raise Exception(f"Unexpected Category name: {category}")


if __name__ == "__main__":
    logger.info(f"{sys.argv[0]} Running")
    run(sys.argv[1], sys.argv[2])