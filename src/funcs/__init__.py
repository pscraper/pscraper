import sys
from const import AppMeta
from logger import Logger


for path in AppMeta.get_sys_appended_path():
    abs_path = r"{}".format(path.absolute())
    Logger.get_logger().info(f"{abs_path} appended to path")
    sys.path.append(abs_path)