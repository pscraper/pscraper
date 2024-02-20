import click
from typing import Any
from classes import Category
from funcs.func_run_adobe import run_adobe
from funcs.func_run_dotnet import run_dotnet
from funcs.func_run_java import run_java
from const import AppMeta



# --phase 1 -> 수집 & 검증 / 엑셀 등록 / 서버 전송 
# --phase 2 -> 엑셀 등록 / 서버 전송 
# --phase 3 -> 서버 전송
# --phase 4 -> 파일 복사
# full command -> pscraper --category {category} --url {url} --phase 1
@click.command(name = AppMeta.APP_NAME)
@click.option("--category", type = click.Choice(["dotnet", "adobe", "java"]))
@click.option("--url", type = click.STRING)
@click.option("--phase", type = click.INT, default = 1)
def main(**kwargs: dict[str, Any]) -> None:    
    category = kwargs["category"]
    DOTNET = Category.DOTNET.lower()
    JAVA = Category.JAVA.lower()
    ADOBE = Category.ADOBE.lower()
    
    if category == DOTNET:
        run_dotnet(**kwargs)
    
    elif category == JAVA:
        run_java(**kwargs)

    elif category == ADOBE:
        run_adobe(**kwargs)

    else:
        raise Exception(f"Unexpected Category name: {category}")
        

if __name__ == "__main__":
    main()
