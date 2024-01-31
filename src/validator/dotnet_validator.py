import os
from validator.validator_manager import ValidatorManager
from const import DOTNET_FILE_PATH, DOTNET_CAB_PATH, logger
from classes import DotnetLocs


class DotnetValidatorManager(ValidatorManager):
    def __init__(self):
        super().__init__()
        
        
    def _check_all_qnumber_file_exists(self, result_dict):
        qnumbers = result_dict.keys()
        validate_set = set()
        
        for file in DOTNET_FILE_PATH.iterdir():
            if not file.name.endswith(".msu"):
                continue
            
            validate_set.add(file.name)
        
        for file_name in validate_set:
            idx = file_name.find("kb")
            qnumber = file_name[(idx + 2):(idx + 9)]
            
            if qnumber not in qnumbers:
                raise Exception(f"{qnumber}에 해당하는 패치 파일이 존재하지 않습니다.")
        
        
    def _check_msu_and_cab_file_exists(self):
        # cab 파일과 msu 파일이 모두 있는지 검사
        for file in os.listdir(DOTNET_FILE_PATH):
            if not file.endswith(".msu"):
                continue

            splt = file.split("-")
            tmp = "-".join([splt[1], splt[2], splt[3]]).replace(".msu", "")
            flag = False

            for cab in os.listdir(DOTNET_CAB_PATH):
                if tmp in cab:
                    logger.info(f"{tmp} -> {cab} 확인")
                    flag = True
                    break
           
            if not flag:
                raise Exception(f"{tmp}에 대한 cab 파일이 확인되지 않습니다.")
            

    # qnumber에 해당하는 아키텍쳐별 패치파일들이 모두 존재하는지 검증해야 한다.
    def _check_all_architecture_file_exists_per_qnumber(self, result_dict):
        logger.info("QNumber에 해당하는 아키텍쳐별 패치파일들이 모두 존재하는지 검증")
        qnumbers = result_dict.keys()
        arch_dict = dict()
        
        for qnumber in qnumbers:
            files = result_dict[qnumber]['files']
            commons = result_dict[qnumber]['common']
            arch_dict[qnumber] = list()
            logger.info(f"[{qnumber}]")
            
            for file in files:
                os_version = commons['os_version']
                excel_key = commons['excel_key']
                architecture = file['architecture']
                arch_dict[qnumber].append((os_version, architecture, excel_key))
                logger.info(f"- {os_version}")
                logger.info(f"- {architecture}")
                
        logger.info("------- 검증 대상 아키텍쳐 목록 구성 완료 -------")
        
        # result.json에서 추출한 excel_key에 해당하는 아키텍쳐가 DotnetLocs.ARCH_DICT에 사전 정의된 아키텍쳐와 모두 동일한지 검증
        last_os_version = ""
        last_excel_key = ""
        arch_set = set()
        
        for qnumber in arch_dict:
            logger.info(f"[{qnumber}] 검증 시작")
            validate_file_list = arch_dict[qnumber]
                
            for file in validate_file_list:
                arch_set.add(file[1])
                last_os_version = file[0]
                last_excel_key = file[-1]
                
            inter_set = arch_set & set(DotnetLocs.ARCH_DICT[last_excel_key])
            
            for inter in inter_set:
                if inter not in DotnetLocs.ARCH_DICT[last_excel_key]:
                    raise Exception(f"{last_os_version}에 대한 {inter} 아키텍쳐 파일이 존재하지 않습니다.")
            
                logger.info(f"- {last_os_version} {last_excel_key} {inter} 확인")
                
    