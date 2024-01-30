import os
from validator_manager import ValidatorManager
from const import DOTNET_FILE_PATH, DOTNET_CAB_PATH, logger


class DotnetValidatorManager(ValidatorManager):
    def __init__(self):
        super().__init__()
        
        
        
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
            
            

    def _check_all_qnumber_file_exists(self, qnumbers):
        file_qnumbers = set()

        for file in os.listdir(DOTNET_FILE_PATH):
            if not file.endswith(".msu"):
                continue

            qnumber = file.split("-")[1][2:]
            file_qnumbers.add(qnumber)

            if qnumber not in qnumbers:
                raise Exception(f"[{qnumber}] 대상 QNumber 포함되지 않은 패치 파일입니다.")

        # 교집합의 여집합이 0개가 되어야 한다.
        diff = file_qnumbers.difference(qnumbers & file_qnumbers)

        if len(diff) != 0:
            raise Exception(f"[{diff}] 수집되지 않은 QNumber가 존재합니다.")