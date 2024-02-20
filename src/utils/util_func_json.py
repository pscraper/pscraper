import json
from const import AppMeta


def save_json_result(path: str, obj: dict):
    with open(path, "w", encoding = AppMeta.ENC_TYPE) as fp:
        kwargs = {"obj": obj, "fp": fp, "indent": 4, "sort_keys": True, "ensure_ascii": False}
        json.dump(**kwargs)
        

def read_json_result(path: str):
    with open(path, "r", encoding = AppMeta.ENC_TYPE) as fp:
        return json.load(fp)