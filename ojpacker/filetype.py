from __future__ import absolute_import

import os
from typing import Dict


class execfile:
    """
    a class save the description of the execute file.  
    you can you macro {src} {exe} in "command" 
    """
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
