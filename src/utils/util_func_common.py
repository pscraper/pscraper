import shutil
import os
from datetime import datetime
from pathlib import Path
from const import PATCH_FILE_PATH, UNREQUIRED_UNICODES, DOTNET_FILE_PATH, RESULT_FILE_PATH, logger
from classes import Category



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


# pathfiles 폴더를 통째로 복사
def copy_file_dir(folder: str) -> bool:
    dst = Path.home() / "Desktop"

    try:
        if os.path.exists(dst / folder):
            shutil.rmtree(dst / folder)

        shutil.copy(DOTNET_FILE_PATH, dst)
        shutil.copy(RESULT_FILE_PATH, dst / "result.json") 
        return True
        
    except Exception as e:
        logger.warn("권한 관련 에러가 발생하여 파일을 복사하지 못하였습니다.")
        logger.warn(e)
        return False
        
        
def remove_file_dir(folder: str) -> bool:
    try:
        if os.path.exists(PATCH_FILE_PATH / folder):
            res = input(f"{str(PATCH_FILE_PATH / folder)} 폴더를 삭제할까요?")
            if res != 'y': 
                return
            
            shutil.rmtree(PATCH_FILE_PATH / folder)
            return True
            
    except Exception as e:
        logger.warning(e)
        return False