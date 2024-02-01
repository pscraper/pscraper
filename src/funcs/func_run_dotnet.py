import subprocess
from validator.dotnet_validator import DotnetValidatorManager
from crawler.dotnet_crawling_manager import DotnetCrawlingManager
from register.dotnet_excel_manager import DotnetExcelManager
from filehandler.dotnet_file_handler import DotnetFileHandler
from utils.util_func_dotnet import update_common_info, update_nation_info, update_file_info, read_mapper_file
from utils.util_func_json import save_json_result
from const import RESULT_FILE_PATH, DATA_PATH, logger



def run_dotnet(url: str, category: str) -> None:
    try:
        _run_dotnet(url, category)
        
    except Exception as e:
        logger.critical("예상치 못한 예외 발생")
        logger.critical(e)
        raise e
                

def _run_dotnet(url: str, category: str) -> None:
    validator = DotnetValidatorManager()
    
    # 패치 데이터 초기화    
    # 해당 과정 이후 최종 선택된 QNumber와 수집 정보들이 mapper.txt에 담긴다.
    crawler = DotnetCrawlingManager(url, category)
    crawler._init_patch_data()
    
    # 공통 정보 가져오기 (CVE, PatchDate, KBNumber, BulletinID)
    patch_date = crawler._get_patch_date()      # 패치 노트 일자를 입력받고 KST 기준으로 변경
    severity = crawler._get_severity()          # 패치의 보안 중요도 정보
    common_cve = crawler._get_cve_string()      # 패치 노트 공통 CVE
    
    # 이 시점에서 각 QNumber에 대한 공통 정보를 result.json 파일에 1차 업데이트 
    # PatchDate, CVE, KBNumber, BulletinID, Catalog Link, OS VERSION, .NET VERSION, EXCEL KEY
    mapper = read_mapper_file()
    result = update_common_info(mapper, patch_date, common_cve, severity)
    save_json_result(RESULT_FILE_PATH, result)
    logger.info(f"{RESULT_FILE_PATH.name}에 공통 정보 업데이트를 완료했습니다.")
    
    # 각 qnumber에 대해 한/영/중/일 title, summary, bulletinUrl 정보 가져오기
    qnumbers = result.keys()
    ts_dict = crawler._get_title_and_summary(patch_date, category, qnumbers)
    
    # ts_dict를 result.json에 반영
    result = update_nation_info(ts_dict, result)
    save_json_result(RESULT_FILE_PATH, result)
    logger.info(f"{RESULT_FILE_PATH.name}에 각 국가별 정보 업데이트를 완료했습니다.")
    
    # 각 qnumber에 대한 patch 파일과 기타 정보 가져오기
    file_dict = crawler._download_patch_file(result, qnumbers)
    result = update_file_info(file_dict, result)
    save_json_result(RESULT_FILE_PATH, result)
    logger.info(f"{RESULT_FILE_PATH.name}에 패치파일 정보 업데이트를 완료했습니다.")
    
    # 수집 대상 qnumber에 대한 모든 msu 패치 파일이 존재하는지 검증
    validator._check_all_qnumber_file_exists(result)
   
    # qnumber에 해당하는 아키텍쳐별 패치파일들이 모두 존재하는지 검증
    validator._check_all_architecture_file_exists_per_qnumber(result)     
    
    # 파일 핸들링 작업 시작
    # 이 시점 이후로 엑셀 등록 전 필요한 모든 정보들이 수집되고, msu 파일명 변경 및 압축 해제, cab 파일명 변경 작업이 이루어진다.
    dfh = DotnetFileHandler()
    dfh.start(result)
    save_json_result(RESULT_FILE_PATH, result)
    
    # msu 파일과 cab 파일의 짝이 맞는지 검사
    # qnumber에 해당하는 아키텍쳐별 패치파일들이 모두 존재하는지 검증해야 한다.
    validator._check_msu_and_cab_file_exists()
    
    # 엑셀 등록 작업 시작
    dem = DotnetExcelManager(category)
    excel_file_name = dem.start()
    
    # 엑셀 파일 오픈
    subprocess.run(
        ["start", "/d", str(DATA_PATH.absolute()), excel_file_name],
        shell = True
    )
    
    logger.info("pscraper Successfully finished")