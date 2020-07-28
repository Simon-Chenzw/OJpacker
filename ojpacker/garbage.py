from __future__ import absolute_import

import os
import shutil
from typing import List

from . import ui

files: List[str] = []


def add(*arg: str) -> None:
    """
    everything should in temporary directory
    """
    for file_name in arg:
        ui.debug(f"add '{file_name}'' to garbage")
        files.append(file_name)


def clean(clean_dir: bool = False) -> None:
    if clean_dir:
        ui.debug("clean up the entire temporary directory")
        shutil.rmtree("temp")
        files.clear()
    else:
        ui.debug("clean garbage", files)
        for file_name in files:
            if not os.path.isfile(file_name):
                ui.warning(f"garbage '{file_name}' not found")
                continue
            os.remove(file_name)
        files.clear()
