from __future__ import absolute_import

import json
import os
import platform

from typing import Dict
from . import ui

# config
defalut_zip_name: str = ""
state_name: str = ""
input_data_name: str = ""
output_data_name: str = ""
input_default_exec: str = ""
output_default_exec: str = ""
input_exec: Dict[str, Dict[str, str]] = {}
output_exec: Dict[str, Dict[str, str]] = {}

config_list = [
    "defalut_zip_name",
    "state_name",
    "input_data_name",
    "output_data_name",
    "input_default_exec",
    "output_default_exec",
    "input_exec",
    "output_exec",
]

# file part
json_name = "ojpacker.json"


def user_setting() -> str:
    """
    unsupport platform return ""
    """
    sys = platform.system().lower()
    if sys == "linux" or sys == "windows":
        return os.path.expanduser(os.path.join("~", ".config", json_name))
    else:
        return ""


def load_setting() -> None:
    if os.path.isfile(json_name):
        setting_json = json_name
    elif os.path.isfile(user_setting()):
        setting_json = user_setting()
    else:
        ui.error("ojpacker.json not found")
        return

    with open(setting_json, "r") as fp:
        try:
            setting: dict = json.load(fp)
        except json.JSONDecodeError:
            ui.error("wrong json format")
            return

    if isinstance(setting, dict):
        for name in config_list:
            globals()[name] = setting.get(name)
    else:
        ui.error("wrong json format")
