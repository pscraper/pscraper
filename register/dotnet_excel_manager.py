from excel_manager import ExcelManager


class DotnetExcelManager(ExcelManager):
    # Sheet 이름
    _sheet_name = "dotnet"

    # 국가 코드 (영/일/한/중)
    nation_code = ["en-us", "ja-jp", "ko-kr", "zh-cn"]

    # .NET Sheet Location
    dotnet_sheet_location = {
        "1607 4.8": {
            # (row, col, row_step)
            "Title": (98, 'B', 4),
            "Summary": (98, 'C', 4),
            "BulletinUrl": (98, 'D', 4),
            '파일명': (103, 'A', 2),
            'SubJect': (103, 'P', 2),
            '파일크기': (103, 'B', 2),
            'MD5': (103, 'J', 2),
            'VendorUrl': (103, 'K', 2),
            'Wsus 파일': (103, 'L', 2),
            "SHA256": (103, 'U', 2),
            "Bulletine ID": (98, 'H', 1),
            'KBNumber': (98, 'I', 1),
            'PatchDate': (98, 'J', 1),
            '중요도': (98, 'K', 1),
            'cve': (100, 'P', 1),
        },

        "1809 3.5 4.7.2": {
            "Title": (107, 'B', 4),
            "Summary": (107, 'C', 4),
            "BulletinUrl": (107, 'D', 4),
            '파일명': (112, 'A', 2),
            'SubJect': (112, 'P', 2),
            '파일크기': (112, 'B', 2),
            'MD5': (112, 'J', 2),
            'VendorUrl': (112, 'K', 2),
            'Wsus 파일': (112, 'L', 2),
            "SHA256": (112, 'U', 2),
            "Bulletine ID": (107, 'H', 1),
            "KBNumber": (107, 'I', 1),
            'PatchDate': (107, 'J', 1),
            '중요도': (107, 'K', 1),
            'cve': (109, 'P', 1),
        },
    }
    
    def __init__(self):
        super().__init__(self._sheet_name)


    def start(self):
        pass


    def run(self):
        print(f"{__class__} 가동을 시작합니다..")

        try:
            self.start()

        except Exception as e:
            print(f"{__class__} 예외가 발생했습니다.")
            print(f"예외 내용: {e}")
    
        finally:
            del self
            print(f"{__class__} 가동을 종료합니다..")


if __name__ == "__main__":
    dem = DotnetExcelManager()
    dem.run()