from register.excel_manager import ExcelManager
from classes import DotnetLocs
from const import logger
from utils.util_func_dotnet import read_mapper_file_and_excel_key_qnumber_dict


class DotnetExcelManager(ExcelManager):
    def __init__(self, category: str):
        super().__init__(category)
        

    def start(self) -> str:
        row = 1
        result_dict = self.result_dict
        key_qnumber_dict = read_mapper_file_and_excel_key_qnumber_dict()

        while True:
            cell_value = self.get_cell_value(row, 'A')
            
            if str(cell_value) == "END":
                self.save_workbook()
                break
            
            if cell_value not in key_qnumber_dict.keys():
                row += 1
                continue
            
            qnumber = str(key_qnumber_dict[cell_value])
            logger.info(f"{qnumber} 엑셀 작업 시작")
            
            # Title, Summary, BulletinUrl 기록
            nations = result_dict[qnumber]['nations']
            self._fill_nations_info(row, nations)
            
            # BulletinID, KBNumber, PatchDate, 중요도, CVE 기록
            commons = result_dict[qnumber]['common']
            self._fill_common_info(row, commons)
        
            # 파일명, 파일크기, MD5, VendorURL, Wsus 파일, SubJect, SHA256 기록
            files = result_dict[qnumber]['files']
            self._fill_patch_info(row, cell_value, files)
            
            # 다음 행으로
            row += 1
        
        logger.info("엑셀 작업 완료")
        return self.save_workbook()
            
            
    def _fill_nations_info(self, row: int, nations: dict[str, dict[str, str]]) -> None:
        for nation in nations:
            infos = nations[nation]
            rel_loc = DotnetLocs.NATION_REL_LOCS[nation]
            
            # 엑셀 파일 (r, c) 위치에 info 각각을 기록
            for info in infos:
                val = infos[info]
                loc = rel_loc[info] 
                r, c = self._calc_relative_locations(row, loc)
                self.set_cell_value(r, c, val)
                logger.info(f"- ({r}, {c}) {val}")
                
        
    
    def _fill_common_info(self, row: int, commons: dict[str, str]) -> None:
        for common in commons:
            if common not in DotnetLocs.KEY_MAPPER:
                continue
            
            loc = DotnetLocs.COMMON_REL_LOCS[DotnetLocs.KEY_MAPPER[common]]
            r, c = self._calc_relative_locations(row, loc)
            val = commons[common]
            self.set_cell_value(r, c, val)      
            logger.info(f"- ({r}, {c}) {val}")
            
    
    def _fill_patch_info(self, row: int, cell_value: str, files: list[dict[str, str]]) -> None:
        for file in files:
            # 엑셀 파일에 해당 아키텍쳐가 있는지 검사
            arch = file['architecture']
            arch_cells = DotnetLocs.ARCH_DICT[cell_value]
            
            if not arch in arch_cells:
                continue
            
            index = arch_cells.index(arch)
            
            for key, val in file.items():
                if key not in DotnetLocs.KEY_MAPPER:
                    continue
                
                loc_key = DotnetLocs.KEY_MAPPER[key]
                loc = DotnetLocs.FILE_REL_LOCS[loc_key]
                r, c = self._calc_relative_locations(row, loc)
                self.set_cell_value(r + index, c, val)
                logger.info(f"- ({r + index}, {c}) {val}")
        
        
    def _calc_relative_locations(self, row: int, loc: tuple[int, int]) -> tuple[int, int]:
        r = row + loc[0]
        c = chr(ord('A') + loc[1])
        return r, c