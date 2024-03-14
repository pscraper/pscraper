## Intro.
<b>pscraper</b>는 Adobe, Oracle, MS 등의 벤더사에서 릴리즈하는 정기/비정기 패치 정보와 패치 파일을 수집하여 검증, 압축 해제, 해시 추출, 엑셀 등록을 자동화한 툴입니다.
.NET Framework와 같은 MS 패치의 경우 패치파일 압축 해제 과정에서 Windows 명령어가 사용되기 때문에, 오직 Windows OS에서만 예외 없는 실행이 가능합니다.
    

---

## Start

### if you clone
```shell
## Create Virtual Env & install packages
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

### Pypi
```shell
python -m pip install pscraper
```

### Options
```shell
pscraper --help
pscraper --category {category} --url {patch_note_url} 
pscraper --category {category} --url {patch_note_url} --phase 1
pscraper --category {category} --url {patch_note_url} --phase 2:5 
```

### Phase (included:included)
- --phase 1 정보 수집 & 검증 단계
- --phase 2 해시 추출 & msu 압축 해제 등 파일 핸들링 단계 
- --phase 3 수집 정보 엑셀 등록 단계
- --phase 4 결과 파일 원격 서버 전송 단계 
- --phase 5 패치 파일 복사 

---

## 파일 
#### result.json 또는 result{date}.json
런타임 중에 수집 정보를 저장하기 위해 만들어지는 json 파일. 
실행마다 새로운 result.json 파일이 만들어지고, 기존 파일은 날짜가 파일명에 추가된다.
(하루가 지난 파일은 실행시 자동 삭제)

#### log.txt 또는 log{date}.txt
런타임 중에 로그를 기록하기 위해 만들어지는 txt 파일.
실행마다 새로운 log.txt 파일이 만들어지고, 기존 파일은 날짜가 파일명에 추가된다.
(하루가 지난 파일은 실행시 자동 삭제) 

#### mapper.txt
런타임 중 각종 정보를 매핑하기 위해 앱 시작 단계에서 초기화되는 파일


#### patch.xlsx
수집 정보가 등록되는 최종 엑셀 파일.


#### chromedriver.exe
크롤링을 작동시키기 위한 크롬드라이버. 
버전 호환이 안되는 경우 아래 링크에서 버전에 맞는 드라이버 설치 필요.
https://chromedriver.chromium.org/downloads

---

## Release
v0.1.0: .NET 패치 수집 기능 제공 <br/>
v0.1.1: .NET 패치 수집 / 검증 / 엑셀 등록 기능 제공

---