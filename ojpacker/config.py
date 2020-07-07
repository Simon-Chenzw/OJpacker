from __future__ import absolute_import

import json
import shutil
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


def load_setting(path: Optional[str] = None) -> None:
    if path:
        if not os.path.isfile(path):
            raise OjpackerError(f"can't find file at {path}")
        setting_json = path
    else:
        if os.path.isfile(json_name):
            setting_json = json_name
            if os.path.isfile(user_setting()):
                ui.info("use local config")
            else:
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


def make_config() -> None:
    ui.info(
        "now only supports setting local configuration to user configuration")
    ui.warning("copy start after 5s")
    ui.countdown(5)
    if not os.path.isfile(json_name):
        raise OjpackerError("local configuration not found")
    if user_setting() == json_name:
        raise OjpackerError(
            "unknown platform, don't know where to store user configuration")
    if os.path.isfile(user_setting()):
        ui.warning("already have user configuration, replace after 5 seconds")
        ui.countdown(5)
    shutil.copyfile(json_name, user_setting())
    ui.info(f"{json_name} has been copied to {user_setting()}")