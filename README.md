## Intro.
<b>pscraper</b>는 Java, Oracle, MS 등의 벤더사에서 릴리즈하는 정기/비정기 패치 정보와 패치 파일을 수집하여 검증, 압축 해제, 해시 추출, 엑셀 등록을 자동화한 툴입니다.
msu 패치파일 압축 해제 과정에서 windows 명령어가 사용되기 때문에, MS 패치의 경우 오직 Windows OS에서만 예외 없는 실행이 가능합니다.
    

---

## Start
```shell
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt

## run
cd src && python pscraper.py {category} {patch_note_url}
```

---

## Release
v0.1.0: .NET 패치 수집 기능 제공
v0.1.1: .NET 패치 수집 / 검증 / 엑셀 등록 기능 제공


---

## Test URL 
- https://devblogs.microsoft.com/dotnet/dotnet-framework-january-2024-security-and-quality-rollup/
- https://devblogs.microsoft.com/dotnet/dotnet-framework-november-2023-security-and-quality-rollup/
- https://devblogs.microsoft.com/dotnet/dotnet-framework-october-2023-security-and-quality-rollup-updates/

---
