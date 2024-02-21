# Adobe 관련 모델
class AdobeCommon:
    PATCH_NOTE_URL = "https://www.adobe.com/devnet-docs/acrobatetk/tools/ReleaseNotesDC/index.html"
    SECURITY_UPDATE_TITLE_FORMAT = "Security update available for Adobe {}({})"
    OPTINAL_UPDATE_TITLE_FORMAT = "Update available for Adobe {}({})({})"
    READER = "Reader"
    ACROBAT = "Acrobat"
    KEY_MAPPER: dict[str, str] = {
        "Adobe Acrobat Reader DC": "Reader",
        "Adobe Acrobat DC": "Acrobat",
        "Adobe Acrobat 2020": "Acrobat"
    }


class AdobeContinuous(AdobeCommon):
    # File Name과 Key를 매핑 
    FK_MAPPER: dict[str, str] = {
        "AcrobatDCUpd": "Adobe Acrobat DC",
        "AcroRdrDCUpd": "Adobe Acrobat Reader DC",
        "AcrobatDCx64Upd": "Adobe Acrobat DC",
        "AcroRdrDCx64Upd": "Adobe Acrobat Reader DC"
    }


class AdobeClassic(AdobeCommon):
    FK_MAPPER: dict[str, str] = {
        "Acrobat2020Upd": "Adobe Acrobat DC 2020"
    }