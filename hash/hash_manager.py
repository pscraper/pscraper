# 작성자: 황승수
# 작성일: 2024/01/04
# 소속: AhnLab EPI 개발팀 PatchLab
# 직급: 인턴


# ---------------- 사용법 --------------------------------------------------
# - 터미널을 "관리자 권한"으로 여는 것을 권장합니다. (파일 읽기/쓰기 권한 문제)
# - 만약, IDEA를 사용한다면 역시 "관리자 권한"으로 여는 것이 좋습니다.
# - 폴더 이름을 Excel 시트의 각 OS 버전 제목과 일치시키기 
# - HashManager._default_path: 패치 파일을 포함하고 있는 루트 디렉터리 경로
# - HashManager._ignore_folders: 탐색을 생략하고자 하는 폴더명
# - HashManager._ignore_files: 탐색을 생략하고자 하는 파일명 
# -------------------------------------------------------------------------


import os
import hashlib


class HashManager:
    # 이 경로 하위에 있는 모든 폴더를 탐색하여 파일을 찾습니다.
    # 해당 파일의 파일명, MD5, SHA256, 파일크기를 추출하고
    # _default_path 경로에 hash.json 파일을 생성하여 추출 정보를 기록합니다.
    _default_path = "C:\\Users\\seungsu\\Desktop\\materials"
    
    # 전체 폴더를 탐색하게 설계되었으므로 
    # 만일 탐색하고 싶지 않은 폴더/파일이 있다면 이곳에 추가
    _ignore_folders = ["icons"]
    _ignore_files = ["CentOS-Stream-8-x86_64-latest-dvd1.iso"]


    def __init__(self, include_files: list, include_folder_name: str):
        self.include_files_name = include_files
        self.include_folder_name = include_folder_name
        self.file_dir_list = os.listdir(self._default_path)
        self.file_path_list = list()
        self.hash_result_list = list()
        self.json_file_path = self._default_path + "\\" + "hash.json"

        if os.path.exists(self.json_file_path):
            self.title_print("기존 hash.json 파일을 삭제합니다")
            os.remove(self.json_file_path)


    def _start(self, path = _default_path):
        if os.path.isfile(path):
            dir, file = os.path.split(path)

            if file in self._ignore_files:
                return
            
            flag = False

            for include_file_name in self.include_files_name:
                flag = file.startswith(include_file_name)
            
                if flag:
                    break
            
            if not flag:
                return
            
            self.file_path_list.append((dir, file))
            print(f"\t파일 발견: {path}")
            return
        
        # 폴더면 한 뎁스 더 들어간다
        list_dir = os.listdir(path)
        dir, file = os.path.split(path)

        if file in self._ignore_folders:
            return

        for f in list_dir:
            print(f"현재 경로: {path}")
            self._start(path + "\\" + f)

    def get_hash_file(self, path: str):
        print(f"[해시값 추출 중......]")
        
        with open(path, "rb") as fp:
            bin = fp.read()
            md5 = hashlib.md5(bin).hexdigest()
            sha256 = hashlib.sha256(bin).hexdigest()
            file_size = f"{os.path.getsize(path) / (10 ** 6):.2f}"

        return md5, sha256, file_size
    
    
    def get_hash_result(self):
        if self.include_folder_name == None:
            self._start()
        else:
            self._start(self.include_folder_name)

        hash_result_list = list()

        for dir, file in self.file_path_list:
            print(f"[작업 중...] dir: {dir}, file: {file}")
            file_path = dir + "\\" + file

            with open(file_path, "rb") as fp:
                binary = fp.read()
                md5 = hashlib.md5(binary).hexdigest()
                sha256 = hashlib.sha256(binary).hexdigest()

                obj = {
                    "dir_path": dir,
                    "file_path": file_path,
                    "file_name": file,
                    "file_size": f"{os.path.getsize(file_path) / (10 ** 6):.2f}",
                    "MD5": md5,
                    "SHA256": sha256
                }

                hash_result_list.append(obj)
        
        del self.file_path_list
        self.title_print("모든 파일에 대한 해시 정보 추출이 완료되었습니다")
        
        return hash_result_list

    
    def title_print(self, msg):
        print("\n")
        print("-" * 30 + msg + "-" * 30)


if __name__ == "__main__":
    hm = HashManager()
