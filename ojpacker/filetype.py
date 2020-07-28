from __future__ import absolute_import

import os
from typing import Dict

from . import config, ui
from .error import OjpackerError
from .ui import log


class execfile:
    """
    a class save the description of the execute file.  
    you can you macro {src} {exe} in "command" 
    """
    @log
    def __init__(self,
                 src: str = "",
                 exe: str = "",
                 compile_cmd: str = "",
                 execute_cmd: str = ""):
        self.src = src
        self.exe = exe or src
        self.compile_cmd = compile_cmd
        self.execute_cmd = execute_cmd

    def get_compile(self, src_dir: str = "", exe_dir: str = "") -> str:
        return self.compile_cmd.format(src=os.path.join(src_dir, self.src),
                                       exe=os.path.join(exe_dir, self.exe))

    def get_execute(self, src_dir: str = "", exe_dir: str = "") -> str:
        return self.execute_cmd.format(src=os.path.join(src_dir, self.src),
                                       exe=os.path.join(exe_dir, self.exe))


def get_execfile(dic: Dict[str, str]) -> execfile:
    return execfile(
        src=dic.get("src", ""),
        exe=dic.get("exe", ""),
        compile_cmd=dic.get("compile_cmd", ""),
        execute_cmd=dic.get("execute_cmd", ""),
    )


class state_file():
    @log
    def __init__(self, name: str) -> None:
        with open(name, "r") as state_file:
            self.lines = tuple(
                map(
                    lambda line: line.rstrip('\n'),
                    state_file.readlines(),
                ))
        if len(self.lines) != 0:
            ui.info(f"{len(self.lines)} line(s) in state")
        else:
            raise OjpackerError("state file is empty")

    def __len__(self) -> int:
        return len(self.lines)

    def __getitem__(self, index: int) -> str:
        return self.lines[index]


class data_file():
    @log
    def __init__(self, origin: str, path: str = "temp") -> None:
        self.origin = origin
        self.path = path

    def __getitem__(self, index: int) -> str:
        return self.origin.format(
            num=index + 1,
            name=config.zip_name,
        )

    def with_path(self, index: int) -> str:
        return os.path.join(self.path, self[index])
