import click
from datetime import datetime
from classes import Category
from funcs.func_run_adobe import run_adobe
from funcs.func_run_dotnet import run_dotnet, _run_dotnet_after_scraping
from funcs.func_run_java import run_java
from utils.util_func_common import remove_before_one_hour_files, add_time_str_to_exists_file_name
from const import APP_NAME, LOG_PATH, DATA_PATH



@click.command(name = APP_NAME)
@click.option("--write_excel", type = click.BOOL, default = False)
@click.option("--category", type = click.Choice(["dotnet", "adobe", "java"]))
@click.option("--url", type = click.STRING, default = "")
def main(category: str, url: str, write_excel: bool) -> None:    
    DOTNET = Category.DOTNET.name.lower()
    JAVA = Category.JAVA.name.lower()
    ADOBE = Category.ADOBE.name.lower()
    
    if category == DOTNET:
        if write_excel:
            _run_dotnet_after_scraping(category)
        else:
            run_dotnet(url, DOTNET)
    
    elif category == JAVA:
        run_java(url, JAVA)

    elif category == ADOBE:
        run_adobe(ADOBE)

    else:
        raise Exception(f"Unexpected Category name: {category}")

    # 로그 파일 및 결과 파일명 날짜 붙여서 변경
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    paths = [LOG_PATH, DATA_PATH]
    for path in paths:
        add_time_str_to_exists_file_name(path, now)
        remove_before_one_hour_files(path, now)
        

if __name__ == "__main__":
    main()
