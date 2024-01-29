import os
import datetime
import json
import openpyxl
import shutil
import yaml
from pathlib import Path


class ExcelManager:
    def __init__(self):
        os.system("cls")

        self._bin_path = Path.cwd() / "bin"
        self._settings_path = self._bin_path / "settings"
        self._excel_file_path = self._settings_path / "patch.xlsx"
        self._json_file_path = self._bin_path / "data" / "result.json"
        self._meta_file_path = self._settings_path / "meta.yaml"
        self.error_string = "{} 파일이 존재하지 않습니다."
        
        # 원본 Excel 파일이 있는지 검사
        if not self._excel_file_path.exists():
            raise Exception(self.error_string.format(self._excel_file_path))

        if not self._json_file_path.exists():
            raise Exception(self.error_string.format(self._json_file_path))
        
        if not self._meta_file_path.exists():
            raise Exception(self.error_string.format(self._meta_file_path))
        
        with open(self._json_file_path, "r", encoding="utf8") as fp:
            self.result_dict = json.load(fp)
            print("JSON 파일 로딩 완료")
            
        with open(self._meta_file_path, "r", encoding="utf8") as fp:
            self.meta_dict = yaml.load(fp, Loader=yaml.FullLoader)
            print("YAML 파일 로딩 완료")

        # 엑셀 파일 copy
        now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.new_excel_file_path = self._settings_path / f"patch{now}.xlsx"
        shutil.copy(self._excel_file_path, self.new_excel_file_path)

        sheet = input("어떤 Sheet를 선택할까요? (dotnet/3rdparty) ")
        
        if sheet == '3rdparty':
            self.patch = input("어떤 패치를 입력할까요? (java/adobe) ")

            if self.patch == "adobe":
                self.adobe_version = input("(Continuos, Classic)")

        self.excel_file = openpyxl.load_workbook(self.new_excel_file_path)
        self.excel_sheet = self.excel_file.get_sheet_by_name(sheet)
        print("엑셀 파일 로딩이 완료되었습니다...")
    

    def get_cell_value(self, row, col: str):
        return self.excel_sheet.cell(row, self._col_to_int(col)).value


    def set_cell_value(self, row, col: str, val):
        self.excel_sheet.cell(row, self._col_to_int(col), val)


    def save_workbook(self):
        self.excel_file.save(self.new_excel_file_path)


    def _col_to_int(self, col: str) -> int:
        val = ord(col) - ord('A') if col.isupper() else ord(col) - ord('a')
        return val + 1
    

if __name__ == "__main__":
    em = ExcelManager()
    # em.save_workbook()
    # em._work_sheet_props()