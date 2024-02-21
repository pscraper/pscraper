import shutil
import requests
from requests_toolbelt import MultipartEncoder
from datetime import datetime
from pathlib import Path
from classes.const import AppMeta, Category
from logger import LogManager


logger = LogManager.get_logger()


# 파일을 전송하기 전 이미 서버에 있는지 체크
def is_exists_on_server(filename: str, category: str, md5: str, sha256: str) -> bool:
    res = requests.head(
        url = AppMeta.REPORT_SERVER_URL + "/file/check",
        params = {
            "filename": filename,
            "category": category,
            "md5": md5,
            "sha256": sha256
        }
    )
    
    return True if res.status_code == 208 else False
    

# 원격 서버로 결과 파일 전송
def upload_file(filepath: Path, category: str) -> requests.Response:
    if not filepath.exists():
        raise Exception(f"Can't Find {filepath}")
    
    body = MultipartEncoder(fields = {
        "file": open(filepath, "rb"),
        "filename": filepath.name,
        "category": category
    })
    
    return requests.post(
        url = AppMeta.REPORT_SERVER_URL + "/file/result",
        data = body,
        headers = {"Content-Type": body.content_type}
    )
    

# 초단위까지 날짜 반환
def get_today_strftime_til_second() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")


# KST 기준으로 날짜 변경
def replace_to_kst(patch_date: str, target: str, category: str) -> str:
    day = patch_date.split('/')[2]
    target_day = str(int(day) - 1)
    splt = target.split('-')

    # 닷넷 제목의 경우 '-'를 기준으로 앞에 한/영/중/일 날짜가 온다
    if category == Category.DOTNET.lower():
        utc_date_str = splt[0].strip()

        if utc_date_str.find(target_day) != -1 and len(splt) == 2:
            splt[0] = utc_date_str.replace(target_day, day)
            return splt[0] + ' - ' + splt[1]
    
    return target
    

def replace_specific_unicode(raw: str) -> str:
    for code in AppMeta.get_replaced_unicodes():
        for key, val in code.items():
            raw = raw.replace(key, val)
            
    return raw


def copy_file_dir(original_path: Path, copy_path: Path) -> None:
    try:
        shutil.copy(original_path, copy_path)
        shutil.copy(AppMeta.RESULT_FILE_PATH, copy_path / "result.json") 
        
    except Exception as e:
        raise e
    
    
# 가장 최신의 log.txt, result.json 파일명을 찾아주는 메서드 
def find_latest_file_name(dir: Path, filename: str, default: Path | None = None) -> Path:
    logger.info(f"{dir} 폴더에서 {filename} 탐색 시작")
    max_num = -1
    max_file = "" 
    
    for file in dir.iterdir():
        if file.name == filename:
            return dir / file.name
    
        if file.name.startswith(filename.split(".")[0]):
            num = int(file.name[file.name.find("2"):file.name.find(".")])
            if num > max_num:
                max_num = num
                max_file = file.name
    
    if max_num == -1 or not max_file:
        if default:
            return default
        raise Exception("최신 파일을 찾을 수 없습니다")
        
    return dir / max_file