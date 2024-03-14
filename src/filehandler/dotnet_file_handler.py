import os
import hashlib
from typing import Any
from logger import LogManager
from classes.const import DirPath, ErrFormat
from pathlib import Path


class DotnetFileHandler:
    def __init__(self):
        self.logger = LogManager.get_logger()
        # cabs 폴더가 없으면 생성
        if not DirPath.CAB.exists():
            self.logger.info(f"{DirPath.CAB} 생성")
            DirPath.CAB.mkdir()

    def start(self, result_dict) -> dict[str, Any]:
        for file in DirPath.DOTNET.iterdir():
            if not file.name.endswith(".msu"):
                continue

            self.logger.info(f"{file.name} 작업 시작")

            # 파일명에서 qnumber 추출
            qnumber = self._extract_qnumber(file.name)

            # 파일명에서 아키텍쳐 추출
            architecture = self._extract_architecture(file.name)

            # ndp 검사
            dotnet_version = result_dict[qnumber]["common"]["dotnet_version"]
            new_name = self._added_ndp_if_not_added(file.name, dotnet_version)

            # 파일명 변경
            new_name = self._msu_file_name_change(new_name)

            if new_name == "ERR":
                self.logger.warn(
                    "중복 파일을 발견하여 해당 파일에 대한 압축 과정을 생략합니다."
                )
                continue

            self.logger.info(f"- {file.name} -> {new_name}")

            # 파일의 MD5, SHA256, SIZE 추출
            md5, sha256, size = self._extract_file_hash(new_name)
            self.logger.info(f"- size: {size}")
            self.logger.info(f"- MD5: {md5}")
            self.logger.info(f"- SHA256: {sha256}")

            # 파일 압축해제
            cab_file_name = self._unzip_msu_file(new_name)

            # 결과 파일 업데이트
            result_dict = self._result_dict_update(
                result_dict,
                qnumber,
                architecture,
                new_name,
                cab_file_name,
                md5,
                sha256,
                size,
            )

        # 불필요한 파일 삭제
        self._remove_unnecessary_files()
        return result_dict

    # 파일명에서 아키텍쳐 추출
    def _extract_architecture(self, filename: str) -> str:
        architectures = ["x64", "x86", "arm64"]
        for architecture in architectures:
            if architecture in filename:
                return architecture

        raise Exception(ErrFormat.cant_find_obj(filename))

    # 결과 파일 업데이트
    def _result_dict_update(
        self,
        result_dict,
        qnumber,
        architecture,
        new_name,
        cab_file_name,
        md5,
        sha256,
        size,
    ):
        files = result_dict[qnumber]["files"]
        obj = {
            "file_name": new_name,
            "subject": new_name,
            "MD5": md5,
            "SHA256": sha256,
            "file_size": size,
            "WSUS 파일": cab_file_name,
        }

        if not files:
            obj.update({"architecture": architecture})
            files.append(obj)
            return result_dict

        for file in files:
            if file["architecture"] == architecture:
                file.update(obj)
                self.logger.info(f"[{qnumber}] {new_name} 파일 정보 업데이트 완료")
                break

        return result_dict

    # 파일명으로부터 qnumber를 추출
    def _extract_qnumber(self, file_name: str) -> str:
        idx = file_name.find("kb")
        if idx == -1:
            idx = file_name.find("KB")

        qnumber = file_name[(idx + 2) : (idx + 9)]
        self.logger.info(f"- {qnumber} 추출")

        return qnumber

    # msu 파일명에서 해시값 제거, kb -> KB
    def _msu_file_name_change(self, file_name: str) -> str:
        new_name = (file_name[: file_name.find("_")] + ".msu").replace("kb", "KB")

        try:
            os.rename(DirPath.DOTNET / file_name, DirPath.DOTNET / new_name)

        except FileExistsError as e:
            self.logger.warn("이미 존재하는 파일입니다.")
            self.logger.warn(e)
            raise e

        return new_name

    # msu 파일 압축 해제
    def _unzip_msu_file(self, file_name: str) -> str:
        # tmp 폴더 접근시 엑세스 거부 예외가 발생할 수 있음
        if file_name.endswith("tmp"):
            return

        cab_file_name = file_name.split(".msu")[0] + "_WSUSSCAN.cab"
        cmd = f"expand -f:* {str(DirPath.DOTNET / file_name)} {str(DirPath.CAB)}"

        try:
            os.system(cmd)
            Path.rename(DirPath.CAB / "WSUSSCAN.cab", DirPath.CAB / cab_file_name)

        except Exception as e:
            self.logger.warning("msu 파일 압축 해제 과정에서 에러 발생")
            self.logger.warning(e)
            raise e

        return cab_file_name

    # 압축 해제 후 불필요한 파일 삭제
    def _remove_unnecessary_files(self):
        for file in DirPath.CAB.iterdir():
            if not file.name.endswith("WSUSSCAN.cab"):
                os.remove(file)
                self.logger.info(f"Remove {file.name}")

    # 파일의 MD5, SHA256, SIZE 추출
    def _extract_file_hash(self, file_name: str) -> tuple[str, str, str]:
        with open(DirPath.DOTNET / file_name, "rb") as fp:
            binary = fp.read()

        md5 = hashlib.md5(binary).hexdigest()
        sha256 = hashlib.sha256(binary).hexdigest()
        size = f"{float(os.path.getsize(DirPath.DOTNET / file_name)) / (2 ** 20):.1f}"

        return md5, sha256, size

    # file_name에 ndp가 붙어있지 않으면 파일명 변경
    def _added_ndp_if_not_added(self, file_name: str, dotnet_version: str) -> str:
        if "ndp" in file_name:
            return file_name

        splt = file_name.split("_")
        versions = ["4.7.2", "4.8.1", "4.8"]  # 4.8을 4.8.1보다 먼저 놓으면 인식되어버림

        for version in versions:
            if version in dotnet_version:
                new_name = (
                    splt[0] + "-ndp" + "".join(version.split(".")) + "_" + splt[-1]
                )
                os.rename(DirPath.DOTNET / file_name, DirPath.DOTNET / new_name)
                self.logger.info(f"No NDP: {file_name} -> {new_name}")
                return new_name

        raise Exception("파일명 변경 과정 중 에러 발생")
