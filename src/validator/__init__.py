from const import FilePath, AppMeta
from classes import DotnetExcel
from logger import Logger


logger = Logger.get_logger()


if not FilePath.MAPPER_FILE_PATH.exists():
    keys = DotnetExcel.ARCH.keys()
    literal = ""
    for key in keys:
        literal += key
        literal += '\n'

    with open(FilePath.MAPPER_FILE_PATH, "w", encoding = AppMeta.ENC_TYPE) as fp:
        fp.write(literal)

    logger.info(f"{FilePath.MAPPER_FILE_PATH.name} 파일 생성")