from __future__ import absolute_import

import json
import os
import shutil
from typing import Any, Dict, List, Optional

from . import filetype, ui
from .error import OjpackerError
from .ui import log

# config
## from json
zip_name: str = ""
state_name: str = ""
input_data_name: str = ""
output_data_name: str = ""
input_exec: Optional[filetype.execfile] = None
output_exec: Optional[filetype.execfile] = None
input_default_exec: str = ""
output_default_exec: str = ""
input_exec_map: Dict[str, Dict[str, str]] = {}
output_exec_map: Dict[str, Dict[str, str]] = {}
## from arg
input_dir: str = "temp"
show_input: bool = False
show_output: bool = False
will_zip: bool = True
zip_list: List[str] = []
max_process: int = -1

# List[src, dst]
config_map: Dict[str, str] = {
    "defalut_zip_name": "zip_name",
    "state_name": "state_name",
    "input_data_name": "input_data_name",
    "output_data_name": "output_data_name",
    "input_default_exec": "input_default_exec",
    "output_default_exec": "output_default_exec",
    "input_exec": "input_exec_map",
    "output_exec": "output_exec_map",
}

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
                ui.detail("use local config")
        elif os.path.isfile(user_setting):
            setting_json = user_setting
            ui.detail("use user config")
        else:
            raise OjpackerError("No user or local configuration found")

    with open(setting_json, "r") as fp:
        try:
            file_setting: Any = json.load(fp)
        except json.JSONDecodeError:
            raise OjpackerError("wrong json format")

    if isinstance(file_setting, dict):
        for name in config_map:
            if name in file_setting:
                globals()[config_map[name]] = file_setting.get(name)
            else:
                ui.detail(f"'{name}' not in json")
        set_input_exec(input_default_exec)
        set_output_exec(output_default_exec)
    else:
        raise OjpackerError("wrong json format")


@log
def set_input_exec(name: str) -> None:
    global input_exec
    if name in input_exec_map:
        input_exec = filetype.get_execfile(input_exec_map[name])
    else:
        input_exec = None


@log
def set_output_exec(name: str) -> None:
    global output_exec
    if name in output_exec_map:
        output_exec = filetype.get_execfile(output_exec_map[name])
    else:
        output_exec = None


@log
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
