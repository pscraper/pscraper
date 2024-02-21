from classes.const import FilePath, AppMeta
from classes.dotnet import DotnetMapper
from logger import LogManager


logger = LogManager.get_logger()


if not FilePath.MAPPER.exists():
    keys = DotnetMapper.ARCH.keys()
    literal = ""
    for key in keys:
        literal += key
        literal += '\n'

    with open(FilePath.MAPPER, "w", encoding = AppMeta.ENC_TYPE) as fp:
        fp.write(literal)

    logger.info(f"{FilePath.MAPPER.name} 파일 생성")