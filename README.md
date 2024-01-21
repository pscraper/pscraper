## pscaper
Java, Oracle, MS 등의 벤더사에서 릴리즈하는 정기/비정기 패치 정보와 패치 파일 및 해시 정보를 자동으로 수집해주는 도구입니다.
업무상 제한된 폐쇄망 환경을 기준으로 개발되었기 때문에 Requests 모듈을 사용하지 못하고, Selenium과 Beautifulsoup을 통해 정보를 수집합니다.
추가적으로 MS 패치의 경우 오직 Windows OS에서만 예외 없는 실행이 가능합니다.

<br/>

"pscraper" automatically collects regular/irregular patch information, patch files, hash information, and various other information from various vendors such as .NET, Adobe, and Java. It was developed for a limited, closed-network business environment, it operates based on Selenium and bs4. Not Requests module. Additionally, when dealing with MS patch files, exception-free execution is only possible on Windows OS.

---

## Run
"run.bat" 파일을 실행하면 배치 작업이 시작됩니다.
배치 작업은 Anaconda를 이용한 Python 가상 환경 세팅, 필요한 라이브러리 설치 및 프로세스 시작을 포함합니다.
만약 Anaconda가 설치되있지 않다면 "main.py" 파일을 직접 실행하여 pscraper를 시작할 수 있습니다.

<br/>

Click the "run.bat" file for batch processing.
The batch process includes creating a virtual environment by Anaconda, downloading required libraries, and scraping.
If your environment doesn't have Anaconda, run "main.py" directly.

** Test URL **
- https://devblogs.microsoft.com/dotnet/dotnet-framework-january-2024-security-and-quality-rollup/
- https://devblogs.microsoft.com/dotnet/dotnet-framework-november-2023-security-and-quality-rollup/
- https://devblogs.microsoft.com/dotnet/dotnet-framework-october-2023-security-and-quality-rollup-updates/

---

## Release
[2024/01/22] v0.1.0: .NET 패치 수집 기능만 제공

