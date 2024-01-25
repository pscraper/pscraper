import os
import sys
import yaml

from excel_manager import ExcelManager


class DotnetExcelManager(ExcelManager):
    def __init__(self):
        super().__init__()

        self.dotnet = self.meta['dotnet']


    def start(self):
        print(self.dotnet)
        print(self.result_dict)


if __name__ == "__main__":
    dem = DotnetExcelManager()
    dem.start()