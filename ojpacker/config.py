from __future__ import absolute_import

import json
import os
import shutil
from typing import Any, Dict, Optional

from . import filetype, ui
from .error import OjpackerError

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
user_setting = os.path.expanduser(os.path.join("~", ".config", json_name))


def load_setting(path: Optional[str] = None) -> None:
    if path:
        if not os.path.isfile(path):
            raise OjpackerError(f"can't find file at {path}")
        setting_json = path
    else:
        if os.path.isfile(json_name):
            setting_json = json_name
            if os.path.isfile(user_setting):
                ui.info("use local config")
            else:
                ui.debug("use local config")
        elif os.path.isfile(user_setting):
            setting_json = user_setting
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


def copyto(copyto: str) -> None:
    if copyto == "user":
        src = json_name
        dst = user_setting
    elif copyto == "local":
        src = user_setting
        dst = json_name
    else:
        raise OjpackerError(f"Unexpected 'copyto' type: {copyto}")
    if os.path.abspath(src) == os.path.abspath(dst):
        raise OjpackerError(f"src is same to dst: {src}")

    ui.info(f"copy {src} to {dst}")
    if not os.path.isfile(src):
        raise OjpackerError(f"{src} not found")
    if os.path.isfile(dst):
        ui.warning(f"already have {dst}, will be replaced")
    ui.info("copy start after 5s")
    ui.countdown(5)
    shutil.copyfile(src, dst)
    ui.info(f"{src} has been copied to {dst}")
