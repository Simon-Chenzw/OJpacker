from __future__ import absolute_import

import os
import shutil

from . import config, ui
from .error import OjpackerError
from .ui import log


@log
def precheck() -> None:
    if config.will_zip:
        if config.zip_name == "":
            raise OjpackerError("zip name is empty")
        for file in config.zip_list:
            if not os.path.isfile(file):
                ui.warning(f"'{file}' in zip_list, does not exist")


@log
def run() -> None:
    def readable_byte(value: float) -> str:
        unit = ["B", "KB", "MB", "GB"]
        level = 0
        while (value >= 1024):
            value /= 1024
            level += 1
        return "%.2f %s" % (value, unit[level])

    # 复制 zip_list
    if config.zip_list:
        for file_name in config.zip_list:
            ui.info(f"copy {file_name} to temporary directory")
            if not os.path.isfile(file_name):
                ui.warning(f"{file_name} not found, skip")
                continue
            shutil.copyfile(file_name, os.path.join("temp", file_name))

    if config.will_zip:
        if os.path.isfile(config.zip_name + ".zip"):
            ui.warning(f"already have {config.zip_name}.zip, remove in 10s")
            ui.countdown(10)
            ui.info(f"remove old {config.zip_name}.zip")
            os.remove(config.zip_name + ".zip")
        ui.info("start compression")
        shutil.make_archive(base_name=config.zip_name,
                            format="zip",
                            root_dir="temp")
        zip_size = readable_byte(os.path.getsize(config.zip_name + ".zip"))
        ui.info(f"compression complete: '{config.zip_name}.zip' {zip_size}")
    else:
        shutil.move("temp", config.zip_name)
        ui.info(f"data has been stored in directory '{config.zip_name}'")
