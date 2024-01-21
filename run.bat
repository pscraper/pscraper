@echo off
REM Anaconda 설치 경로
set ANACONDA_DIR=%HOMEPATH%\anaconda3

REM 가상 환경 이름 세팅
set ENV_NAME=pscraper

REM 파이썬 버전 지정
set PYTHON_VERSION=3.10

REM 가상 환경 생성 
if not exist "%ANACONDA_DIR%\envs\%ENV_NAME%" (
    "%ANACONDA_DIR%\Scripts\conda" create --name %ENV_NAME% python=%PYTHON_VERSION% -y
) else (
    echo Virtual env %ENV_NAME% already exists.
)

REM 가상 환경 Activate
call "%ANACONDA_DIR%\Scripts\activate" %ENV_NAME%

REM bs4, selenium 설치 확인, 없으면 설치
call "%ANACONDA_DIR%\Scripts\conda" list -n %ENV_NAME% | findstr "beautifulsoup4" > .\bin\test.log
set /p var=<.\bin\test.log
echo %var%

if "%var:beautifulsoup4=%" neq "%var%" (
    call "%ANACONDA_DIR%\Scripts\conda" install -n %ENV_NAME% -c conda-forge beautifulsoup4 -y
) 

del .\bin\test.log

call "%ANACONDA_DIR%\Scripts\conda" list -n %ENV_NAME% | findstr "selenium" > .\bin\test.log
set /p var=<.\bin\test.log

if "%var:selenium=%" neq "%var%" (
    call "%ANACONDA_DIR%\Scripts\conda" install -n %ENV_NAME% -c conda-forge selenium -y
) else (
    echo %var%
)

del .\bin\test.log

call python main.py

pause