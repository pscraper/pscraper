from enum import Enum
from typing import Any


class Category(Enum):
    DOTNET = "Dotnet"
    JAVA = "Java"
    ADOBE = "Adobe"


class AdobeCommon:
    SECURITY_UPDATE_TITLE_FORMAT = "Security update available for Adobe {}({})"
    OPTINAL_UPDATE_TITLE_FORMAT = "Update available for Adobe {}({})({})"
    READER = "Reader"
    ACROBAT = "Acrobat"
    
    KEY_MAPPER: dict[str, str] = {
        "Adobe Acrobat Reader DC": "Reader",
        "Adobe Acrobat DC": "Acrobat",
        "Adobe Acrobat 2020": "Acrobat"
    }


class AdobeContinuous:
    # File Name과 Key를 매핑 
    FK_MAPPER: dict[str, str] = {
        "AcrobatDCUpd": "Adobe Acrobat DC",
        "AcroRdrDCUpd": "Adobe Acrobat Reader DC",
        "AcrobatDCx64Upd": "Adobe Acrobat DC",
        "AcroRdrDCx64Upd": "Adobe Acrobat Reader DC"
    }


class AdobeClassic:
    FK_MAPPER: dict[str, str] = {
        "Acrobat2020Upd": "Adobe Acrobat DC 2020"
    }


class DotnetLocs:
    # 엑셀 파일 내 상대위치
    NATION_REL_LOCS: dict[str, dict[str, tuple[int, int]]] = {
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
    COMMON_REL_LOCS: dict[str, tuple[int, int]] = {
        "BulletinID": (1, 7),
        "KBNumber": (1, 8),
        "PatchDate": (1, 9),
        "중요도": (1, 10),
        "cve": (3, 15)
    }

    # 파일명, 파일크기, MD5, VendorURL, Wsus 파일, SubJect, SHA256 상대 위치
    # 파일이 여러개인 경우 열은 고정, 행 + 1
    FILE_REL_LOCS: dict[str, tuple[int, int]] = {
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
    KEY_MAPPER: dict[str, str] = {
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
    ARCH_DICT: dict[str, list[str]] = {
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
    
    