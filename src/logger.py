import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from const import AppMeta, DirPath 


class Logger:
    LOG_PATH = DirPath.BIN_PATH / "logs"
    LOG_FILE_PATH = LOG_PATH / "log.txt"  # 프로그램 실행 중 로깅을 위한 파일
    DEFAULT_REMOVE_HOUR = 5000   # 30분
    _logger_ = None
    
    def __init__(self):
        # 로그 파일 및 결과 파일명 날짜 붙여서 변경
        if self._logger_ == None:
            self._logger_ = self.get_logger()

        now = datetime.now().strftime("%Y%m%d%H%M%S")
        for path in [self.LOG_PATH, DirPath.DATA_PATH]:
            self.add_time_str_to_exists_file_name(path, now)
            self.remove_before_one_hour_files(path, now)
    
    @classmethod
    def get_logger(cls) -> logging:
        if cls._logger_ == None:
            stdout_handler = logging.StreamHandler(stream = sys.stdout)                # 콘솔 출력을 위한 핸들러
            file_handler = logging.FileHandler(cls.LOG_FILE_PATH, encoding = AppMeta.ENC_TYPE)     # 파일 출력을 위한 핸들러
            logging.basicConfig(
                level = logging.INFO,
                format = '%(asctime)s %(levelname)s: [%(module)s.%(funcName)s] %(message)s',
                datefmt = '[%m/%d/%Y %I:%M:%S] %p',
                handlers = [stdout_handler, file_handler]
            )
            cls._logger_ = logging
            
        return cls._logger_
    
    def remove_before_one_hour_files(self, path: Path, now: str):
        for file in path.iterdir():
            if not (
                file.name.startswith("log2") or 
                file.name.startswith("result2") or 
                file.name.startswith("patch2")):
                continue
            
            time_str = file.name[file.name.find('2'):file.name.find('.')]
            if int(now) - int(time_str) >= self.DEFAULT_REMOVE_HOUR:
                os.remove(path / file)
                self._logger_.info(f"Remove Old File: {file}")
            
    def add_time_str_to_exists_file_name(self, path: Path, now: str):
        for file in path.iterdir():
            name = file.name
            if not (name == "result.json" or name == "log.txt"):
                continue

            name_splt = name.split('.')
            new_name = name_splt[0] + now + '.' + name_splt[1]
            os.rename(path / file, path / new_name)
            self._logger_.info(f"{file} -> {new_name}")
            
        
