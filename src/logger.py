import logging
import sys
import os
from logging import Logger
from datetime import datetime
from pathlib import Path
from classes.const import AppMeta, DirPath, FilePath


class LogManager:
    DEFAULT_REMOVE_HOUR = 5000   # 30분
    _logger_ = None
    
    
    @classmethod
    def init_cls(cls):
        if cls._logger_ == None:
            cls._logger_ = logging.getLogger()
        
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        for path in [DirPath.LOG, DirPath.DATA]:
            cls.add_time_str_to_exists_file_name(path, now)
            cls.remove_before_one_hour_files(path, now)
    
        logging.basicConfig(
            level = logging.INFO,
            format = '%(asctime)s %(levelname)s: [%(module)s.%(funcName)s] %(message)s',
            datefmt = '[%m/%d/%Y %I:%M:%S] %p',
            handlers = [
                logging.StreamHandler(stream = sys.stdout),
                logging.FileHandler(filename = FilePath.LOG, encoding = AppMeta.ENC_TYPE)
            ]
        )
    
    
    @classmethod
    def get_logger(cls) -> Logger:
        return cls._logger_
    
    
    @classmethod
    def remove_before_one_hour_files(cls, path: Path, now: str):
        for file in path.iterdir():
            if not (
                file.name.startswith("log2") or 
                file.name.startswith("result2") or 
                file.name.startswith("patch2")):
                continue
            
            time_str = file.name[file.name.find('2'):file.name.find('.')]
            if int(now) - int(time_str) >= cls.DEFAULT_REMOVE_HOUR:
                os.remove(path / file)
                cls._logger_.info(f"Remove Old File: {file}")
            
    
    @classmethod
    def add_time_str_to_exists_file_name(cls, path: Path, now: str):
        for file in path.iterdir():
            name = file.name
            if not (name == "result.json" or name == "log.txt"):
                continue

            name_splt = name.split('.')
            new_name = name_splt[0] + now + '.' + name_splt[1]
            os.rename(path / file, path / new_name)
            cls._logger_.info(f"{file} -> {new_name}")
            
        
