from const import (
    MAPPER_FILE_PATH,
    ENC_TYPE,
    DOTNET_KB_FORMAT as KB_FORMAT,
    DOTNET_BULLETIN_FORMAT as BULLETIN_FORMAT,
    logger
)



def extract_qnumber_from_kb_file_name(file_name: str) -> str:
    idx = extract_idx_from_file_name(file_name, "kb")
    return file_name[(idx + 2):(idx + 9)]
    
    
def extract_qnumber_from_KB_file_name(file_name: str) -> str:
    idx = extract_idx_from_file_name(file_name, "KB")
    return file_name[(idx + 2):(idx + 9)]


def extract_idx_from_file_name(file_name: str, find_str: str) -> int:
    idx = file_name.find(find_str)
    
    if idx == -1:
        raise Exception(f"파일명에서 {find_str} 추출 불가")
    
    return idx


def read_mapper_file() -> list[list[str]]:
    with open(MAPPER_FILE_PATH, "r", encoding = ENC_TYPE) as fp:
        lines = list(map(lambda x: x.strip(), fp.readlines()))
        logger.info(f"{MAPPER_FILE_PATH.name} 로딩 완료")
    
        # lines 분리 (QNumber | OS Version | .NET Version | Catalog Link | Excel Key)
        for idx, line in enumerate(lines):
            lines[idx] = list(map(lambda x: x.strip(), line.split("|")))    

    return lines


def read_mapper_file_and_transform_dict() -> dict[str, dict[str, str]]:
    result = dict()
    mappers = read_mapper_file()

    for mapper in mappers:
        result[mapper[0]] = {
            "os_version": mapper[1],
            "dotnet_version": mapper[2],
            "catalog_link": mapper[3],
            "excel_key": mapper[4]
        }

    return result


def read_mapper_file_and_transform_qnumber_set() -> set[str]:
    qnumbers = set()
    mappers = read_mapper_file()

    for mapper in mappers:
        qnumbers.add(mapper[0])
    
    return qnumbers


def read_mapper_file_and_excel_key_qnumber_dict() -> dict[str, str]:
    key_qnumber_dict = dict()
    mappers = read_mapper_file()
    
    for mapper in mappers:
        key_qnumber_dict[mapper[-1]] = mapper[0]

    return key_qnumber_dict


def update_common_info(lines: list[list[str]], patch_date: str, common_cve: str, severity: str) -> None:
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
            "bulletin_id": BULLETIN_FORMAT.format(qnumber),
            "severity": severity
        }
        
    return result


def update_nation_info(ts_dict, result):
    for qnumber in ts_dict.keys():
        result[qnumber]['nations'] = dict()
        
        for nation in ts_dict[qnumber]:
            result[qnumber]['nations'][nation] = dict()
            result[qnumber]['nations'][nation]['bulletin_url'] = ts_dict[qnumber][nation]['bulletin_url']
            result[qnumber]['nations'][nation]['title'] = ts_dict[qnumber][nation]['title']
            result[qnumber]['nations'][nation]['summary'] = ts_dict[qnumber][nation]['summary']
        
    return result
        

def update_file_info(file_dict, result):
    for qnumber in file_dict:
        result[qnumber]['files'] = list()
    
        for file in file_dict[qnumber]:
            file_name: str = file['file_name']
            idx = file_name.find("kb") + 2
            fqnumber = file_name[(idx):(idx + 7)]
        
            if qnumber == fqnumber:
                result[qnumber]['files'].append(file) 
            
    return result