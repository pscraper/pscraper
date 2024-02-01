from datetime import datetime
from const import UNREQUIRED_UNICODES
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