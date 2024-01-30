import json
from util_func_json import save_json_result
from const import (
    RESULT_FILE_PATH,
    MAPPER_FILE_PATH,
    UNREQUIRED_UNICODES,
    ENC_TYPE,
    DOTNET_KB_FORMAT as KB_FORMAT,
    DOTNET_BULLETIN_FORMAT as BULLETIN_FORMAT,
    logger
)



def replace_specific_unicode(raw: str) -> str:
    for code in UNREQUIRED_UNICODES:
        for key, val in code.items():
            raw = raw.replace(key, val)
            
    return raw



def read_mapper_file() -> list[list[str]]:
    with open(MAPPER_FILE_PATH, "r", encoding = ENC_TYPE) as fp:
        lines = list(map(lambda x: x.strip(), fp.readlines()))
        logger.info(f"{MAPPER_FILE_PATH.name} 로딩 완료")
    
        # lines 분리 (QNumber | OS Version | .NET Version | Catalog Link | Excel Key)
        for idx, line in enumerate(lines):
            lines[idx] = list(map(lambda x: x.strip(), line.split("|")))    

    return lines
    


def update_common_info(lines: list[list[str]], patch_date: str, common_cve: str) -> None:
    # result.json 공통 정보 쓰기
    result = dict()
    
    for line in lines:
        qnumber = line[0]
        os_version = line[1]
        dotnet_version = line[2]
        catalog_link = line[3]
        excel_key = line[4]
        
        result[qnumber] = dict()
        result[qnumber]['common'] = {
            "patch_date": patch_date,
            "common_cve": common_cve,
            "os_version": os_version,
            "dotnet_version": dotnet_version,
            "catalog_link": catalog_link,
            "excel_key": excel_key,
            "kb_number": KB_FORMAT.format(qnumber),
            "bulletin_id": BULLETIN_FORMAT.format(qnumber)
        }
    
    save_json_result(RESULT_FILE_PATH, result)
        