import os
import shutil
import hashlib
from const import DOTNET_FILE_PATH, DOTNET_CAB_PATH, RESULT_FILE_PATH, logger
from pathlib import Path



class DotnetFileHandler:
    def __init__(self):
        # cabs 폴더가 없으면 생성
        if not DOTNET_CAB_PATH.exists():
            logger.info(f"{DOTNET_CAB_PATH} 생성")
            DOTNET_CAB_PATH.mkdir()


    def start(self, result_dict):
        for file in DOTNET_FILE_PATH.iterdir():
            if not file.name.endswith(".msu"):
                continue

            if "ndp" not in file.name:
                logger.warn(f"No NDP: {file.name}")
                continue
            
            # 파일명에서 qnumber 추출
            qnumber = self._extract_qnumber(file.name)

            # 파일명에서 아키텍쳐 추출
            architecture = self._extract_architecture(file.name)
            
            # 파일명 변경
            self._msu_file_name_change(file.name)
 
            # 파일의 MD5, SHA256, SIZE 추출
            md5, sha256, size = self._extract_file_hash(file.name)

            # 파일 압축해제
            self._unzip_msu_file()

            # 결과 파일 업데이트
            self._result_dict_update(result_dict, qnumber, architecture, md5, sha256, size)

        # 불필요한 파일 삭제
        self._remove_unnecessary_files()

        # 바탕화면으로 결과 폴더 복사
        self._copy_file_dir()


    # 결과 파일 업데이트
    def _result_dict_update(self, result_dict, qnumber, architecture, md5, sha256, size):
        files = result_dict[qnumber]['files']
        
        for file in files:
            if file['architecture'] == architecture:
                file.update({
                    "MD5": md5,
                    "SHA256": sha256,
                    "file_size": size
                })
            
            break


    # 파일명으로부터 qnumber를 추출
    def _extract_qnumber(self, file_name: str) -> str:
        idx = file_name.find("kb")
        if idx == -1:
            raise Exception("파일명에서 QNumber를 추출할 수 없습니다.")
        
        return file_name[(idx + 2):(idx + 9)]


    # msu 파일명에서 해시값 제거, kb -> KB 
    def _msu_file_name_change(self, file_name: str):
        new_name = (file_name[:file_name.find('_')] + ".msu").replace("kb", "KB")
        os.rename(file_name, new_name)
      

    # msu 파일 압축 해제
    def _unzip_msu_file(self, file_name: str):
        # tmp 폴더 접근시 엑세스 거부 예외가 발생할 수 있음
        if file_name.endswith("tmp"):
            return

        cab_file_name = file_name.split(".msu")[0] + "_WSUSSCAN.cab" 
        cmd = f"expand -f:* {str(DOTNET_FILE_PATH / file_name)} {str(DOTNET_CAB_PATH)}"
        
        try:
            os.system(cmd)
            Path.rename(DOTNET_CAB_PATH / "WSUSSCAN.cab", DOTNET_CAB_PATH / cab_file_name)
        
        except Exception as e:    
            logger.warning("msu 파일 압축 해제 과정에서 에러 발생")
            logger.warning(e)
            raise e

    
    # 압축 해제 후 불필요한 파일 삭제
    def _remove_unnecessary_files(self):
        for file in DOTNET_CAB_PATH.iterdir():
            if not file.name.endswith("WSUSSCAN.cab"):
                os.remove(file)
                logger.info(f"Remove {file.name}")
    

   # pathfiles/dotnet 폴더를 통째로 복사
    def _copy_file_dir(self):
        dst = Path.home() / "Desktop"

        if os.path.exists(dst / "dotnet"):
            shutil.rmtree(dst / "dotnet")

        shutil.move(DOTNET_FILE_PATH, dst)
        shutil.copy(RESULT_FILE_PATH, dst / "result.json") 


    # 파일의 MD5, SHA256, SIZE 추출
    def _extract_file_hash(self, file_name: str) -> tuple[str, str, str]:
        with open(DOTNET_FILE_PATH / file_name, "rb") as fp:
            binary = fp.read()
        
        md5 = hashlib.md5(binary).hexdigest()
        sha256 = hashlib.sha256(binary).hexdigest()
        size = f"{float(os.path.getsize(DOTNET_FILE_PATH / file_name)) / (2 ** 20):.1f}"

        return md5, sha256, size