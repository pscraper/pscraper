import subprocess
import shutil
import os
import hashlib
from pathlib import Path
from validator.dotnet_validator import DotnetValidatorManager
from crawler.dotnet_crawling_manager import DotnetCrawlingManager
from register.dotnet_excel_manager import DotnetExcelManager
from filehandler.dotnet_file_handler import DotnetFileHandler
from utils.util_func_dotnet import (
    update_common_info,
    update_nation_info,
    update_file_info,
    read_mapper_file,
)
from utils.util_func_json import read_json_result, save_json_result
from utils.util_func_common import (
    copy_file_dir,
    is_exists_on_server,
    upload_file,
    find_latest_file_name,
)
from classes.const import FilePath, DirPath
from logger import LogManager


logger = LogManager.get_logger()


def run_dotnet(category: str, url: str, phase: str) -> None:
    err = False
    run_name = category.upper()
    validator = DotnetValidatorManager()
    splt = phase.split(":")

    if len(splt) == 2:
        start_phase = int(splt[0])
        end_phase = int(splt[1])

    else:
        start_phase = int(splt[0])
        end_phase = 5

    try:
        if start_phase <= 1:
            logger.info(f"[Phase 1] {run_name} 수집 & 검증 단계를 시작합니다.")
            _run_dotnet_phase1(validator, url, category)

        if end_phase >= 2:
            logger.info(
                f"[Phase 2] {run_name} 해시 추출 & msu 압축 해제 & 파일명 변경 작업을 시작합니다."
            )
            _run_dotnet_phase2(validator)

        if end_phase >= 3:
            logger.info(f"[Phase 3] {run_name} 엑셀 등록 작업을 시작합니다.")
            _run_dotnet_phase3(category)

        if end_phase >= 4:
            logger.info(f"[Phase 4] {run_name} 리포트 서버에 결과를 보고합니다.")
            _run_dotnet_phase4(category)

        if end_phase >= 5:
            logger.info(f"[Phase 5] {run_name} 패치 파일을 바탕화면으로 복사합니다.")
            _run_dotnet_phase5(category)

    except Exception as e:
        logger.critical("예상치 못한 예외 발생")
        logger.critical(e)
        err = True

    finally:
        if err:
            exit(1)
        logger.info("pscraper Successfully finished")


def _run_dotnet_phase1(
    validator: DotnetValidatorManager, url: str, category: str
) -> None:
    crawler = DotnetCrawlingManager(url, category)

    # 패치 데이터 초기화
    # 해당 과정 이후 최종 선택된 QNumber와 수집 정보들이 mapper.txt에 담긴다.
    crawler._init_patch_data()

    # 공통 정보 가져오기 (CVE, PatchDate, KBNumber, BulletinID)
    patch_date = (
        crawler._get_patch_date()
    )  # 패치 노트 일자를 입력받고 KST 기준으로 변경
    severity = crawler._get_severity()  # 패치의 보안 중요도 정보
    common_cve = crawler._get_cve_string()  # 패치 노트 공통 CVE

    # 이 시점에서 각 QNumber에 대한 공통 정보를 result.json 파일에 1차 업데이트
    # PatchDate, CVE, KBNumber, BulletinID, Catalog Link, OS VERSION, .NET VERSION, EXCEL KEY
    mapper = read_mapper_file()
    result = update_common_info(mapper, patch_date, common_cve, severity)
    save_json_result(FilePath.RESULT, result)
    logger.info(f"{FilePath.RESULT.name}에 공통 정보 업데이트를 완료했습니다.")

    # 각 qnumber에 대해 한/영/중/일 title, summary, bulletinUrl 정보 가져오기
    qnumbers = result.keys()
    ts_dict = crawler._get_title_and_summary(patch_date, category, qnumbers)

    # ts_dict를 result.json에 반영
    result = update_nation_info(ts_dict, result)
    save_json_result(FilePath.RESULT, result)
    logger.info(f"{FilePath.RESULT.name}에 각 국가별 정보 업데이트를 완료했습니다.")

    # 각 qnumber에 대한 patch 파일과 기타 정보 가져오기
    file_dict = crawler._download_patch_file(result, qnumbers)
    result = update_file_info(file_dict, result)
    save_json_result(FilePath.RESULT, result)
    logger.info(f"{FilePath.RESULT.name}에 패치파일 정보 업데이트를 완료했습니다.")

    # 수집 대상 qnumber에 대한 모든 msu 패치 파일이 존재하는지 검증
    validator._check_all_qnumber_file_exists(result)

    # qnumber에 해당하는 아키텍쳐별 패치파일들이 모두 존재하는지 검증
    validator._check_all_architecture_file_exists_per_qnumber(result)


# 파일 핸들링 작업 단계
# --phase 2
def _run_dotnet_phase2(validator: DotnetValidatorManager) -> None:
    # result 파일이 없는 경우 가장 최신 파일을 복사
    if not FilePath.RESULT.exists():
        filename = find_latest_file_name(DirPath.DATA, "result.json")
        shutil.copy(DirPath.DATA / filename, FilePath.RESULT)
        logger.info(f"[COPY] {filename} -> {FilePath.RESULT.name}")

    result = read_json_result(FilePath.RESULT)

    # 중복 파일이 있는지 검사하고 있으면 삭제
    for file in DirPath.DOTNET.iterdir():
        if "(" in file.name and ")" in file.name:
            logger.info(f"[DELETE] 중복 파일 {file.name}")
            file.unlink()

    # 파일 핸들링 작업 시작
    # 이 시점 이후로 엑셀 등록 전 필요한 모든 정보들이 수집되고, msu 파일명 변경 및 압축 해제, cab 파일명 변경 작업이 이루어진다.
    dfh = DotnetFileHandler()
    result = dfh.start(result)
    save_json_result(FilePath.RESULT, result)

    # msu 파일과 cab 파일의 짝이 맞는지 검사
    # qnumber에 해당하는 아키텍쳐별 패치파일들이 모두 존재하는지 검증해야 한다.
    validator._check_msu_and_cab_file_exists()


# 엑셀 등록 과정부터 시작하기
# 이미 모든 패치 파일 및 정보가 수집된 이후
# --phase 3
def _run_dotnet_phase3(category: str) -> None:
    # result 파일이 없는 경우 가장 최신 파일을 복사
    if not FilePath.RESULT.exists():
        filename = find_latest_file_name(DirPath.DATA, "result.json")
        shutil.copy(DirPath.DATA / filename, FilePath.RESULT)
        logger.info(f"[COPY] {filename} -> {FilePath.RESULT.name}")

    # cab 폴더가 없거나 빈 경우
    if not DirPath.CAB.exists() or not os.listdir(DirPath.CAB):
        filehandler = DotnetFileHandler()
        validator = DotnetValidatorManager()
        result = filehandler.start(read_json_result(FilePath.RESULT))
        validator._check_msu_and_cab_file_exists()
        save_json_result(FilePath.RESULT, result)

    # 엑셀 등록 작업 시작
    dem = DotnetExcelManager(category)
    excel_file_name = dem.start()

    # 엑셀 파일 오픈
    subprocess.run(
        ["start", "/WAIT", "/d", str(DirPath.DATA.absolute()), excel_file_name],
        shell=True,
    )


def _run_dotnet_phase4(category: str) -> None:
    result_file = find_latest_file_name(DirPath.DATA, "result.json")
    excel_file = find_latest_file_name(
        DirPath.DATA, "patch.xlsx", default=DirPath.EXE / "patch.xlsx"
    )
    mapper_file = find_latest_file_name(DirPath.DATA, "mapper.txt")
    log_file = find_latest_file_name(DirPath.LOG, "log.txt")

    for path in [result_file, excel_file, mapper_file, log_file]:
        try:
            with open(path, "rb") as fp:
                binary = fp.read()
                logger.info(f"{path.name} 해시 추출 중")
                md5 = hashlib.md5(binary).hexdigest()
                sha256 = hashlib.sha256(binary).hexdigest()
                logger.info(f"- {md5}")
                logger.info(f"- {sha256}")

            if is_exists_on_server(path.name, category, md5, sha256):
                logger.info(f"중복된 파일 업로드 제외: {path.name}")
                continue

            res = upload_file(path, category)
            res.raise_for_status()

            if res.status_code == 200:
                logger.info(f"{path} 업로드 완료")

        except Exception as e:
            logger.critical(e)


def _run_dotnet_phase5(category: str) -> None:
    dst = Path.cwd() / category
    copy_file_dir(original_path=DirPath.DOTNET, copy_path=dst)
