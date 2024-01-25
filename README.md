## Intro.
<b>"pscraper"</b>는 Java, Oracle, MS 등의 벤더사에서 릴리즈하는 정기/비정기 패치 정보와 패치 파일 및 해시 정보를 자동으로 수집해주는 도구입니다. <br/>
업무상 제한된 폐쇄망 환경을 기준으로 개발되었기 때문에 Selenium과 Beautifulsoup을 통해 정보를 수집합니다.
추가적으로 MS 패치의 경우 오직 Windows OS에서만 예외 없는 실행이 가능합니다.
    

---

## How to
환경에 따라 다음 세 가지 방법을 제공합니다.

### 1. batch file 실행
"run.bat" 파일을 실행하면 배치 작업이 시작됩니다.
배치 작업은 Anaconda를 이용한 Python 가상 환경 세팅, 필요한 라이브러리 설치 및 프로세스 시작을 포함합니다.
    

<br/>

### 2. exe 파일 실행
dist 폴더 내 "main.exe" 파일 또는, 우측 새롭게 Release된 exe 실행 파일을 다운로드 받아 <b>pscraper</b>를 실행할 수 있습니다.
해당 방법은 Python 런타임 환경이 필요 없기 때문에 특히 유용하고 패치 파일 및 수집 정보는 "%APPDATA%\Local\Temp" 경로에 생성됩니다. 
    

<br/>

### 3. 직접 실행
만약 Anaconda가 설치되있지 않거나, exe 파일을 실행할 수 없는 환경이라면 "main.py" 파일을 직접 실행하여 <b>pscraper</b>를 작동할 수 있습니다.


---

## Test URL 
- https://devblogs.microsoft.com/dotnet/dotnet-framework-january-2024-security-and-quality-rollup/
- https://devblogs.microsoft.com/dotnet/dotnet-framework-november-2023-security-and-quality-rollup/
- https://devblogs.microsoft.com/dotnet/dotnet-framework-october-2023-security-and-quality-rollup-updates/

---
