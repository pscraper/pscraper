import os
import shutil
import hashlib
from const import DOTNET_FILE_PATH, DOTNET_CAB_PATH, RESULT_FILE_PATH, ERR_ARCH_FORMAT, logger
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

            logger.info(f"{file.name} 작업 시작")
            
            # 파일명에서 qnumber 추출
            qnumber = self._extract_qnumber(file.name)

            # 파일명에서 아키텍쳐 추출
            architecture = self._extract_architecture(file.name)
            
            # ndp 검사
            dotnet_version = result_dict[qnumber]['common']['dotnet_version']
            new_name = self._added_ndp_if_not_added(file.name, dotnet_version)
            
            # 파일명 변경
            new_name = self._msu_file_name_change(new_name)
            
            if new_name == 'ERR':
                logger.warn("중복 파일을 발견하여 해당 파일에 대한 압축 과정을 생략합니다.")
                continue
            
            logger.info(f"- {file.name} -> {new_name}")
 
            # 파일의 MD5, SHA256, SIZE 추출
            md5, sha256, size = self._extract_file_hash(new_name)
            logger.info(f"- size: {size}")
            logger.info(f"- MD5: {md5}")
            logger.info(f"- SHA256: {sha256}")

            # 파일 압축해제
            cab_file_name = self._unzip_msu_file(new_name)

            # 결과 파일 업데이트
            self._result_dict_update(result_dict, qnumber, architecture, new_name, cab_file_name, md5, sha256, size)

        # 불필요한 파일 삭제
        self._remove_unnecessary_files()

        # 바탕화면으로 결과 폴더 복사
        self._copy_file_dir()

    
    # 파일명에서 아키텍쳐 추출
    def _extract_architecture(self, file_name: str) -> str:
        architectures = ['x64', 'x86', 'arm64']
        
        for architecture in architectures:
            if architecture in file_name:
                return architecture
            
        raise Exception(ERR_ARCH_FORMAT.format(file_name))
        

    # 결과 파일 업데이트
    def _result_dict_update(self, result_dict, qnumber, architecture, new_name, cab_file_name, md5, sha256, size):
        files = result_dict[qnumber]['files']
        
        for file in files:
            if file['architecture'] == architecture:
                file.update({
                    "file_name": new_name,
                    "subject": new_name,
                    "MD5": md5,
                    "SHA256": sha256,
                    "file_size": size,
                    "WSUS 파일": cab_file_name
                })
                
                logger.info(f"[{qnumber}] {new_name} 파일 정보 업데이트 완료")
                break


    # 파일명으로부터 qnumber를 추출
    def _extract_qnumber(self, file_name: str) -> str:
        idx = file_name.find("kb")
        if idx == -1:
            raise Exception("파일명에서 QNumber를 추출할 수 없습니다.")
        
        qnumber = file_name[(idx + 2):(idx + 9)]
        logger.info(f"- {qnumber} 추출")
        
        return qnumber


    # msu 파일명에서 해시값 제거, kb -> KB 
    def _msu_file_name_change(self, file_name: str) -> str:
        new_name = (file_name[:file_name.find('_')] + ".msu").replace("kb", "KB")
        
        try:
            os.rename(DOTNET_FILE_PATH / file_name, DOTNET_FILE_PATH / new_name)
            
        except FileExistsError as e:
            logger.warn("이미 존재하는 파일입니다.")
            logger.warn(e)
            return "ERR"
            
        return new_name
    

    # msu 파일 압축 해제
    def _unzip_msu_file(self, file_name: str) -> str:
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
        
        return cab_file_name

    
    # 압축 해제 후 불필요한 파일 삭제
    def _remove_unnecessary_files(self):
        for file in DOTNET_CAB_PATH.iterdir():
            if not file.name.endswith("WSUSSCAN.cab"):
                os.remove(file)
                logger.info(f"Remove {file.name}")
    

   # pathfiles/dotnet 폴더를 통째로 복사
    def _copy_file_dir(self):
        dst = Path.home() / "Desktop"

        try:
            if os.path.exists(dst / "dotnet"):
                shutil.rmtree(dst / "dotnet")

            shutil.copy(DOTNET_FILE_PATH, dst)
            shutil.copy(RESULT_FILE_PATH, dst / "result.json") 
            
        except Exception as e:
            logger.warn("권한 관련 에러가 발생하여 파일을 이동하지 못하였습니다.")
            logger.warn(e)


    # 파일의 MD5, SHA256, SIZE 추출
    def _extract_file_hash(self, file_name: str) -> tuple[str, str, str]:
        with open(DOTNET_FILE_PATH / file_name, "rb") as fp:
            binary = fp.read()
        
        md5 = hashlib.md5(binary).hexdigest()
        sha256 = hashlib.sha256(binary).hexdigest()
        size = f"{float(os.path.getsize(DOTNET_FILE_PATH / file_name)) / (2 ** 20):.1f}"

        return md5, sha256, size
    
    
    # file_name에 ndp가 붙어있지 않으면 파일명 변경
    def _added_ndp_if_not_added(self, file_name: str, dotnet_version: str) -> str:
        if "ndp" in file_name:
            return file_name
        
        splt = file_name.split('_')
        versions = ["4.7.2", "4.8.1", "4.8"]        # 4.8을 4.8.1보다 먼저 놓으면 인식되어버림
        
        for version in versions:
            if version in dotnet_version:
                new_name = splt[0] + "-ndp" + "".join(version.split(".")) + "_" + splt[-1]
                os.rename(DOTNET_FILE_PATH / file_name, DOTNET_FILE_PATH / new_name)
                logger.info(f"No NDP: {file_name} -> {new_name}")
                return new_name 

        raise Exception("파일명 변경 과정 중 에러 발생")