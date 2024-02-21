from register.excel_manager import ExcelManager


class AdobeExcelManager(ExcelManager):

    def __init__(self, category: str):
        super().__init__(category)


if __name__ == "__main__":
    aem = AdobeExcelManager()