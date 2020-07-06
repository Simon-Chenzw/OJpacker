from __future__ import absolute_import

import json
import os
import platform
from typing import Any, Dict, Optional

from ojpacker.error import OjpackerError

from . import filetype, ui

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
        return json_name


def load_setting() -> None:
    if os.path.isfile(json_name):
        setting_json = json_name
        ui.debug("use local config")
    elif os.path.isfile(user_setting()):
        setting_json = user_setting()
        ui.debug("use user config")
    else:
        raise OjpackerError("No user or local configuration found")

    with open(setting_json, "r") as fp:
        try:
            file_setting: Any = json.load(fp)
        except json.JSONDecodeError:
            raise OjpackerError("wrong json format")

    if isinstance(file_setting, dict):
        for name in config_list:
            globals()[name] = file_setting.get(name)
    else:
        raise OjpackerError("wrong json format")


def get_input_exec(name: str) -> Optional[filetype.execfile]:
    if name in input_exec:
        return filetype.get_execfile(input_exec[name])
    else:
        return None


def get_output_exec(name: str) -> Optional[filetype.execfile]:
    if name in output_exec:
        return filetype.get_execfile(output_exec[name])
    else:
        return None
