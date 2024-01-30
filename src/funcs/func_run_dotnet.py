from validator.dotnet_validator import DotnetValidatorManager
from crawler.dotnet_crawling_manager import DotnetCrawlingManager
from register.dotnet_excel_manager import DotnetExcelManager
from filehandler.dotnet_file_handler import DotnetFileHandler
from utils.util_func_dotnet import update_common_info, read_mapper_file
from utils.util_func_json import read_json_result, save_json_result
from const import (
    MAPPER_FILE_PATH,
    RESULT_FILE_PATH,
    ENC_TYPE,
    logger
)


def run_dotnet(url: str, category: str):
    validator = DotnetValidatorManager()
    
    # 패치 데이터 초기화    
    # 해당 과정 이후 최종 선택된 QNumber와 수집 정보들이 mapper.txt에 담긴다.
    crawler = DotnetCrawlingManager(url, category)
    crawler._init_patch_data()
    
    # 공통 정보 가져오기 (CVE, PatchDate, KBNumber, BulletinID), 중요도는 추후 update
    patch_date = crawler._get_patch_date()      # TODO 패치 노트 일자 -> KST로 변경 필수
    common_cve = crawler._get_cve_string()      # 패치 노트 공통 CVE
    
    # 이 시점에서 각 QNumber에 대한 공통 정보를 result.json 파일에 1차 업데이트 
    # PatchDate, CVE, KBNumber, BulletinID, Catalog Link, OS VERSION, .NET VERSION, EXCEL KEY
    mapper = read_mapper_file()
    update_common_info(mapper, patch_date, common_cve)
    logger.info(f"{RESULT_FILE_PATH.name}에 공통 정보 업데이트를 완료했습니다.")
    
    # 패치 수집에 해당하는 QNumber를 얻어오기 위해 result.json 파일 읽기
    result = read_json_result(RESULT_FILE_PATH)
    qnumbers = result.keys()
    
    # 각 qnumber에 대해 한/영/중/일 title, summary, bulletinUrl 정보 가져오기
    ts_dict = crawler._get_title_and_summary(qnumbers)
    
    # ts_dict를 result.json에 반영
    for qnumber in ts_dict.keys():
        result[qnumber]['nations'] = dict()
        
        for nation in ts_dict[qnumber]:
            result[qnumber]['nations'][nation] = dict()
            result[qnumber]['nations'][nation]['bulletin_url'] = ts_dict[qnumber][nation]['bulletin_url']
            result[qnumber]['nations'][nation]['title'] = ts_dict[qnumber][nation]['title']
            result[qnumber]['nations'][nation]['summary'] = ts_dict[qnumber][nation]['summary']
    
    save_json_result(RESULT_FILE_PATH, result)
    logger.info(f"{RESULT_FILE_PATH.name}에 각 국가별 정보 업데이트를 완료했습니다.")
    
    # 각 qnumber에 대한 patch 파일과 기타 정보 가져오기
    result = read_json_result(RESULT_FILE_PATH)
    file_dict = crawler._download_patch_file(result, qnumbers)
    print(file_dict)
    
    for qnumber in file_dict:
        result[qnumber]['files'] = list()
        
        for file in file_dict[qnumber]:
            result[qnumber]['files'].append(file)
            
    save_json_result(RESULT_FILE_PATH, result)
    logger.info(f"{RESULT_FILE_PATH.name}에 패치파일 정보 업데이트를 완료했습니다.")
    
    # 수집 대상 qnumber에 대한 모든 msu 패치 파일이 존재하는지 검사
    validator._check_all_qnumber_file_exists(qnumbers)     
    
    # 파일 핸들링 작업 시작
    result = read_json_result(RESULT_FILE_PATH)
    dfh = DotnetFileHandler()
    dfh.start(result)
    
    # msu 파일과 cab 파일의 짝이 맞는지 검사
    validator._check_msu_and_cab_file_exists()

    # 엑셀 등록 작업 시작
    dem = DotnetExcelManager(category)
    dem.start()
    
              