import sys
import os
from classes import Category
from const import (
    SYS_APPENDED_PATHS,
    logger
)


# conda activate {env_name}
# python pscraper.py {Category} {url}
def run(category: str, url: str) -> None:
    os.system("cls")
    
    DOTNET = Category.DOTNET.name.lower()
    JAVA = Category.JAVA.name.lower()
    ADOBE = Category.ADOBE.name.lower()
    
    if category == DOTNET:
        run_dotnet(url)
    
    elif category == JAVA:
        run_java(url)

    elif category == ADOBE:
        run_adobe(url)

    else:
        raise Exception(f"Unexpected Category name: {category}")


if __name__ == "__main__":
    for path in SYS_APPENDED_PATHS:
        abs_path = r"{}".format(path.absolute())
        logger.debug(f"path appended to sys: {abs_path}")
        sys.path.append(abs_path)

    from runner.func_run_adobe import run_adobe
    from runner.func_run_dotnet import run_dotnet
    from runner.func_run_java import run_java

    category = sys.argv[1]
    url = sys.argv[2]

    run(category, url)