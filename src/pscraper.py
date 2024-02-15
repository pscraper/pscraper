import click
from classes import Category
from const import APP_NAME
from funcs.func_run_adobe import run_adobe
from funcs.func_run_dotnet import run_dotnet, _run_dotnet_after_scraping
from funcs.func_run_java import run_java



@click.command(name = APP_NAME)
@click.option("--write_excel", default = False)
@click.option("--category", type = click.Choice(["dotnet", "adobe", "java"]))
@click.option("--url", type = click.STRING)
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
        run_adobe(url, ADOBE)

    else:
        raise Exception(f"Unexpected Category name: {category}")
    

if __name__ == "__main__":
    main()