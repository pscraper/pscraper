import sys
from classes.const import AppMeta
from logger import LogManager


LogManager.init_cls()


for path in AppMeta.get_sys_appended_path():
    abs_path = r"{}".format(path.absolute())
    LogManager.get_logger().info(f"{abs_path} appended to path")
    sys.path.append(abs_path)