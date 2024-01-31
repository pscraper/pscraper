import subprocess
import os
from datetime import datetime
from validator.dotnet_validator import DotnetValidatorManager
from crawler.dotnet_crawling_manager import DotnetCrawlingManager
from register.dotnet_excel_manager import DotnetExcelManager
from filehandler.dotnet_file_handler import DotnetFileHandler
from utils.util_func_dotnet import update_common_info, read_mapper_file
from utils.util_func_json import read_json_result, save_json_result
from const import RESULT_FILE_PATH, DATA_PATH, LOG_PATH, logger


def run_dotnet(url: str, category: str) -> None:
    try:
        _run_dotnet(url, category)
        
    except Exception as e:
        logger.critical("예상치 못한 예외 발생")
        logger.critical(e)
        raise e
    
    finally:
        now = datetime.today().strftime("%Y%m%d%H%M%s")
    
        # 로그 파일명 날짜 붙여서 변경
        new_log_file_name = "log" + now + ".txt"
        os.rename(LOG_PATH / "log.txt", LOG_PATH / new_log_file_name)
    
        # result.json 파일명 날짜, 시간 붙여서 변경
        new_result_file_name = "result" + now + ".json"
        os.rename(RESULT_FILE_PATH, DATA_PATH / new_result_file_name)        
                


def _run_dotnet(url: str, category: str) -> None:
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
    crawler._wait_til_download_ended()
    
    for qnumber in file_dict:
        result[qnumber]['files'] = list()
        
        for file in file_dict[qnumber]:
            file_name: str = file['file_name']
            idx = file_name.find("kb") + 2
            fqnumber = file_name[(idx):(idx + 7)]
            
            if qnumber == fqnumber:
                result[qnumber]['files'].append(file)
            
    save_json_result(RESULT_FILE_PATH, result)
    logger.info(f"{RESULT_FILE_PATH.name}에 패치파일 정보 업데이트를 완료했습니다.")
    
    # 수집 대상 qnumber에 대한 모든 msu 패치 파일이 존재하는지 검증
    validator._check_all_qnumber_file_exists(result)
   
    # qnumber에 해당하는 아키텍쳐별 패치파일들이 모두 존재하는지 검증
    validator._check_all_architecture_file_exists_per_qnumber(result)     
    
    # 파일 핸들링 작업 시작
    # 이 시점 이후로 엑셀 등록 전 필요한 모든 정보들이 수집되고, msu 파일명 변경 및 압축 해제, cab 파일명 변경 작업이 이루어진다.
    result = read_json_result(RESULT_FILE_PATH)
    dfh = DotnetFileHandler()
    dfh.start(result)
    save_json_result(RESULT_FILE_PATH, result)
    
    # msu 파일과 cab 파일의 짝이 맞는지 검사
    # qnumber에 해당하는 아키텍쳐별 패치파일들이 모두 존재하는지 검증해야 한다.
    validator._check_msu_and_cab_file_exists()
    
    
    # TODO 후속작업 (패치 일자, 중요도, 타이틀에서 날짜 바꾸기 등)
    # 해당 메서드는 최상위 validator에 두기
    

    # 엑셀 등록 작업 시작
    dem = DotnetExcelManager(category)
    excel_file_name = dem.start()
    
    # 엑셀 파일 오픈
    subprocess.run(
        ["start", "/WAIT", "/d", str(DATA_PATH.absolute()), excel_file_name],
        shell = True
    )
    
    logger.info("pscraper Successfully finished")
    return