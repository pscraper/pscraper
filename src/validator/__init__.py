from const import MAPPER_FILE_PATH, ENC_TYPE, logger
from classes import DotnetLocs


if not MAPPER_FILE_PATH.exists():
    keys = DotnetLocs.ARCH_DICT.keys()
    
    literal = ""
    
    for key in keys:
        literal += key
        literal += '\n'

    with open(MAPPER_FILE_PATH, "w", encoding = ENC_TYPE) as fp:
        fp.write(literal)

    logger.info(f"{MAPPER_FILE_PATH.name} 파일 생성")