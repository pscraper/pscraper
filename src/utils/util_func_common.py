import shutil
import requests
from requests_toolbelt import MultipartEncoder
from datetime import datetime
from pathlib import Path
from classes import Category
from const import UNREQUIRED_UNICODES, RESULT_FILE_PATH, REPORT_SERVER_URL



# 원격 서버로 결과 파일 전송
def upload_result_file(path: Path) -> requests.Response:
    if not path.exists():
        raise Exception("Can't Find Result file")
    
    body = MultipartEncoder(fields = {
        'file': open(path, "rb")
    })
    
    return requests.post(
        url = REPORT_SERVER_URL,
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
    if category == Category.DOTNET.name.lower():
        utc_date_str = splt[0].strip()

        if utc_date_str.find(target_day) != -1 and len(splt) == 2:
            splt[0] = utc_date_str.replace(target_day, day)
            return splt[0] + ' - ' + splt[1]
    
    return target
    

def replace_specific_unicode(raw: str) -> str:
    for code in UNREQUIRED_UNICODES:
        for key, val in code.items():
            raw = raw.replace(key, val)
            
    return raw


def copy_file_dir(original_path: Path, copy_path: Path) -> None:
    try:
        shutil.copy(original_path, copy_path)
        shutil.copy(RESULT_FILE_PATH, copy_path / "result.json") 
        
    except Exception as e:
        raise e