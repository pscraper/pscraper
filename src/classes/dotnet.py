from typing import Any


# DOTNET DOM STRINGS
class DotnetDOM:
    CVE_STR = r"CVE-\d+-\d+"
    CVE_ID = r"^cve"
    KB_STR = r"^KB\\d{7}"
    PF_DOWNLOAD = "//*[@id=\"downloadFiles\"]"
    TS_HEADER = "page-header"      # Title_and_Summary Header ID
    TS_SUMMARY = "bkmk_summary"    # Title_and_Summary Summary ID
    
    
# .NET 관련 공통 메타 정보
class DotnetCommon:
    NATION_LIST = ['en-us', 'ja-jp', 'ko-kr', 'zh-cn']
    
    
# .NET 관련 공통 포멧
class DotnetFormat:
    _KB_NUMBER = "KB{}"
    _BULLETIN_ID = "MS-KB{}"
    _BULLETIN_URL = "https://support.microsoft.com/{}/help/{}"
    
    @classmethod
    def get_kb_number(cls, qnumber: str) -> str:
        return cls._KB_NUMBER.format(qnumber)
    
    @classmethod
    def get_bulletin_id(cls, qnumber: str) -> str:
        return cls._BULLETIN_ID.format(qnumber)
    
    @classmethod
    def get_bulletin_url(cls, nation: str, qnumber: str) -> str:
        return cls._BULLETIN_URL.format(nation, qnumber)
    
    
# .NET Excel과 앱의 Mapper 역할을 하는 클래스
class DotnetMapper:
        # 엑셀 파일과 json 파일의 키를 맞추기 위한 Mapper
    KEY: dict[str, str] = {
        "MD5": "MD5",
        "SHA256": "SHA256",
        "WSUS 파일": "Wsus 파일",
        "architecture": "Bit Type Flag",
        "file_name": "파일명",
        "file_size": "파일크기",
        "vendor_url": "VendorUrl",
        "subject": "SubJect",
        "bulletin_id": "BulletinID",
        "common_cve": "cve",
        "kb_number": "KBNumber",
        "patch_date": "PatchDate",
        "severity": "중요도"
    }

    # Architecture 정보
    ARCH: dict[str, Any] = {
        "11 22H2, 23H2 3.5, 4.8.1": ["x64", "arm64"],
        "11 21H2 3.5, 4.8": ["x64", "arm64"],
        "11 21H2 3.5, 4.8.1": ["x64", "arm64"],
        "2022 3.5, 4.8": ["x64"],
        "2022 3.5, 4.8.1": ["x64"],
        "10 21H2, 22H2 3.5, 4.8": ["x86", "x64", "arm64"],
        "10 21H2, 22H2 3.5, 4.8.1": ["x64", "x86"],
        "1809 3.5, 4.7.2": ["x86", "x64"],
        "1809 3.5, 4.8": ["x64", "x86"],
        "1607 4.8": ["x86", "x64"]
    }
    
    
# .NET 엑셀 상대 위치를 갖고 있는 클래스 
class DotnetExcel:    
    NATIONS: dict[str, Any] = {
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
    COMMONS: dict[str, Any] = {
        "BulletinID": (1, 7),
        "KBNumber": (1, 8),
        "PatchDate": (1, 9),
        "중요도": (1, 10),
        "cve": (3, 15)
    }

    # 파일명, 파일크기, MD5, VendorURL, Wsus 파일, SubJect, SHA256 상대 위치
    # 파일이 여러개인 경우 열은 고정, 행 + 1
    FILES: dict[str, Any] = {
        "파일명": (6, 0),
        "파일크기": (6, 1),
        "MD5": (6, 9),
        "VendorUrl": (6, 10),
        "Wsus 파일": (6, 11),
        "Bit Type Flag": (6, 14),
        "SubJect": (6, 15),
        "SHA256": (6, 20)
    }