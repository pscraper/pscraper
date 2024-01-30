import sys
from const import SYS_APPENDED_PATHS, logger


for path in SYS_APPENDED_PATHS:
    abs_path = r"{}".format(path.absolute())
    logger.info(f"{abs_path} appended to path")
    sys.path.append(abs_path)