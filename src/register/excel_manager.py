import json
import openpyxl
import shutil
from utils.util_func_common import get_today_strftime_til_second
from classes import Category
from const import (
    DATA_PATH,
    EXCEL_FILE_PATH,
    RESULT_FILE_PATH,
    ENC_TYPE,
    ERR_STR_FORMAT,
    logger
)


class ExcelManager:
    def __init__(self, category: str):
        # 원본 Excel 파일이 있는지 검사
        if not EXCEL_FILE_PATH.exists():
            raise Exception(ERR_STR_FORMAT.format(EXCEL_FILE_PATH))

        if not RESULT_FILE_PATH.exists():
            raise Exception(ERR_STR_FORMAT.format(RESULT_FILE_PATH))
        
        with open(RESULT_FILE_PATH, "r", encoding = ENC_TYPE) as fp:
            self.result_dict = json.load(fp)
            logger.info("JSON 파일 로딩 완료")
            
        # 엑셀 파일 copy
        now = get_today_strftime_til_second()
        self.new_excel_file_path = DATA_PATH / f"patch{now}.xlsx"
        shutil.copy(EXCEL_FILE_PATH, self.new_excel_file_path)

        # sheet 이름 
        if category == Category.DOTNET.name.lower():
            sheet = category
        else:
            sheet = "3rdparty"
            
        self.excel_file = openpyxl.load_workbook(self.new_excel_file_path)
        self.excel_sheet = self.excel_file.get_sheet_by_name(sheet)
        logger.info(f"{sheet} 시트 오픈")
        logger.info("엑셀 파일 로딩 완료")
    

    def get_cell_value(self, row, col: str):
        return self.excel_sheet.cell(row, self._col_to_int(col)).value


    def set_cell_value(self, row, col: str, val):
        self.excel_sheet.cell(row, self._col_to_int(col), val)


    def save_workbook(self) -> str:
        self.excel_file.save(self.new_excel_file_path)
        return self.new_excel_file_path


    def _col_to_int(self, col: str) -> int:
        val = ord(col) - ord('A') if col.isupper() else ord(col) - ord('a')
        return val + 1