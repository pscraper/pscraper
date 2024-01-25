from excel_manager import ExcelManager


class AdobeExcelManager(ExcelManager):
    _sheet_name = "3rdparty"

    def __init__(self):
        super().__init__(self._sheet_name)


if __name__ == "__main__":
    aem = AdobeExcelManager()