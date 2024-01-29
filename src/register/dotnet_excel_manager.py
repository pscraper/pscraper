import yaml
from excel_manager import ExcelManager


class DotnetExcelManager(ExcelManager):
    # 엑셀 파일 내 상대위치
    nation_rel_locs: dict[str, dict[str, tuple[int, int]]] = {
        "en-us": {
            "title": (1, 1),
            "summary": (1, 2),
            "bulletin_url": (1, 3)
        },
        
        "ja-jp": {
            "title": (2, 1),
            "summary": (2, 2),
            "bulletin_url": (2, 3)
        },
        
       "ko-kr": {
            "title": (3, 1),
            "summary": (3, 2),
            "bulletin_url": (3, 3)
        },

        "zh-cn": {
            "title": (4, 1),
            "summary": (4, 2),
            "bulletin_url": (4, 3)
        },
    }
    
    # BulletinID, KBNumber, PatchDate, 중요도, CVE 상대 위치
    common_rel_locs: dict[str, tuple[int, int]] = {
        "BulletinID": (1, 7),
        "KBNumber": (1, 8),
        "PatchDate": (1, 9),
        "중요도": (1, 10),
        "cve": (3, 15)
    }
    
    # 파일명, 파일크기, MD5, VendorURL, Wsus 파일, SubJect, SHA256 상대 위치
    # 파일이 여러개인 경우 열은 고정, 행 + 1
    files_rel_locs: dict[str, tuple[int, int]] = {
        "파일명": (6, 0),
        "파일크기": (6, 1),
        "MD5": (6, 9),
        "VendorUrl": (6, 10),
        "Wsus 파일": (6, 11),
        "Bit Type Flag": (6, 14),
        "SubJect": (6, 15),
        "SHA256": (6, 20)
    }
    
    # 엑셀 파일과 json 파일의 키를 맞추기 위한 Mapper
    files_mapper = {
        "MD5": "MD5",
        "SHA256": "SHA256",
        "WSUS 파일": "Wsus 파일",
        "architecture": "Bit Type Flag",
        "file_name": "파일명",
        "file_size": "파일크기",
        "vendor_url": "VendorUrl",
        "subject": "SubJect"
    }
    
    # Architecture 정보
    arch_dict: dict[str, list[str]] = {
        "1607 4.8": ["x86", "x64"],
        "1809 3.5, 4.7.2": ["x86", "x64"],
        "1809 3.5, 4.8": ["x64", "x86"],
        "10 21H2, 22H2 3.5, 4.8": ["x86", "x64", "arm64"],
        "10 21H2, 22H2 3.5, 4.8.1": ["x64", "x86"],
        "2022 3.5, 4.8": ["x64"],
        "2022 3.5, 4.8.1": ["x64"],
        "11 21H2 3.5, 4.8": ["x64", "arm64"],
        "11 21H2 3.5, 4.8.1": ["x64", "arm64"],
        "11 22H2, 23H2 3.5, 4.8.1": ["x64", "arm64"]
    }
    
    
    def __init__(self):
        super().__init__()
        self.dotnet = self.meta_dict['dotnet']
        mapper_file_path = self._settings_path / "mapper.yaml"
        
        if not mapper_file_path.exists():
            raise Exception(self.error_string.format(mapper_file_path))
        
        with open(mapper_file_path, "r", encoding="utf8") as fp:
            self.mapper = yaml.load(fp, Loader = yaml.FullLoader)
        

    def start(self):
        row = 1
        result_dict = self.result_dict
        
        while True:
            cell_value = self.get_cell_value(row, 'A')
            
            if str(cell_value) == "END":
                self.save_workbook()
                break
            
            if cell_value not in self.mapper.keys():
                row += 1
                continue
            
            qnumber = str(self.mapper[cell_value])
            print(f"[{qnumber}]{cell_value} 진행 중....")
            
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
        
        print("작업 완료...")
            
            
    def _fill_nations_info(self, row: int, nations: dict[str, dict[str, str]]) -> None:
        for nation in nations:
            infos = nations[nation]
            rel_loc = self.nation_rel_locs[nation]
            
            # 엑셀 파일 (r, c) 위치에 info 각각을 기록
            for info in infos:
                val = infos[info]
                loc = rel_loc[info] 
                r, c = self._calc_relative_locations(row, loc)
                self.set_cell_value(r, c, val)
        
    
    def _fill_common_info(self, row: int, commons: dict[str, str]) -> None:
        for common in commons:
            loc = self.common_rel_locs[common]
            r, c = self._calc_relative_locations(row, loc)
            val = commons[common]
            self.set_cell_value(r, c, val)      
            
    
    def _fill_patch_info(self, row: int, cell_value: str, files: list[dict[str, str]]) -> None:
        for file in files:
            arch = file['architecture']
            
            # 엑셀 파일에 해당 아키텍쳐가 있는지 검사
            arch_cells = self.arch_dict[cell_value]
            index = arch_cells.index(arch)
            
            for key, val in file.items():
                if key not in self.files_mapper:
                    continue
                
                loc_key = self.files_mapper[key]
                loc = self.files_rel_locs[loc_key]
                r, c = self._calc_relative_locations(row, loc)
                self.set_cell_value(r + index, c, val)

        
    def _calc_relative_locations(self, row: int, loc: tuple[int, int]) -> tuple[int, int]:
        r = row + loc[0]
        c = chr(ord('A') + loc[1])
        return r, c
    
            
if __name__ == "__main__":
    dem = DotnetExcelManager()
    dem.start()