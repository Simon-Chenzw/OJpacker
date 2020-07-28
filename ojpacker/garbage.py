from __future__ import absolute_import

import os
import shutil
from typing import List

from . import ui
from .ui import log

files: List[str] = []


@log
def add(*arg: str) -> None:
    """
    everything should in temporary directory
    """
    for file_name in arg:
        files.append(file_name)


@log
def clean(clean_dir: bool = False) -> None:
    if clean_dir:
        shutil.rmtree("temp")
        files.clear()
    else:
        ui.detail("garbage:", *files)
        for file_name in files:
            if not os.path.isfile(file_name):
                ui.warning(f"garbage '{file_name}' not found")
                continue
            os.remove(file_name)
        files.clear()
