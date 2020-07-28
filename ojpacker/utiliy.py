from __future__ import absolute_import

import os
import shlex
import subprocess
import time
from typing import List, Optional

from typing_extensions import Literal

from . import ui
from .error import OjpackerError
from .ui import log


class popen:
    @log
    def __init__(
            self,
            cmd: str,
            typ: Literal["s2s", "s2f", "f2f"] = "s2s",
            input: Optional[str] = None,
            output: Optional[str] = None,
            capture_output: bool = True,
            check_return: bool = True,
            max_time: Optional[int] = None,
    ) -> Optional[str]:
        self.cmd = cmd
        self.typ = typ
        self.input = input
        self.output = output
        self.capture_output = capture_output
        self.check_return = check_return
        self.max_time = max_time
        self.is_start = False

    @log
    def start(self) -> None:
        if self.typ == "s2s":
            self.popen = subprocess.Popen(
                shlex.split(self.cmd),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE if self.capture_output else None,
                stderr=subprocess.STDOUT if self.capture_output else None,
                universal_newlines=True,
            )
            if self.input:
                self.popen.stdin.write(self.input)
            self.popen.stdin.close()
        elif self.typ == "s2f":
            if self.output:
                self.file_out = open(self.output, 'w')
            else:
                raise OjpackerError("popen: need input file, but get nothing")
            self.popen = subprocess.Popen(
                shlex.split(self.cmd),
                stdin=subprocess.PIPE,
                stdout=self.file_out,
                stderr=None,
                universal_newlines=True,
            )
            if self.input:
                self.popen.stdin.write(self.input)
            self.popen.stdin.close()
        elif self.typ == "f2f":
            if self.input:
                self.file_in = open(self.input, 'r')
            else:
                raise OjpackerError("popen: need input file, but get nothing")
            if self.output:
                self.file_out = open(self.output, 'w')
            else:
                raise OjpackerError("popen: need output file, but get nothing")
            self.popen = subprocess.Popen(
                shlex.split(self.cmd),
                stdin=self.file_in,
                stdout=self.file_out,
                stderr=None,
                universal_newlines=True,
            )
        self.is_start = True
        self.start_time = time.time()

    def check(self) -> bool:
        """
        Check whether it is completed, and close the file. 
        if it's completed, check the returncode and raise NonZeroExit
        """
        if not self.is_start:
            return False
        returncode = self.popen.poll()
        if returncode is None:
            return False
        if self.typ[0] == 'f':
            self.file_in.close()
        if self.typ[2] == 'f':
            self.file_out.close()
        if (not self.check_return) or returncode == 0:
            return True
        else:
            raise OjpackerError(
                f"Command '{self.cmd}' returned non-zero exit status {returncode}"
            )

    def join(self) -> None:
        """
        wait until time out. will raise Timeout or NonZeroExit
        """
        if self.check():
            return
        if not self.is_start:
            self.start()
        pass_time = time.time() - self.start_time
        if self.max_time and pass_time > self.max_time:
            raise OjpackerError(
                f"Command '{self.cmd}' timed out after {int(pass_time)} seconds"
            )
        try:
            self.popen.wait(
                timeout=self.max_time and (self.max_time - pass_time))
            self.check()
        except subprocess.TimeoutExpired:
            raise OjpackerError(
                f"Command '{self.cmd}' timed out after {int(time.time() - self.start_time)} seconds"
            )

    def halt(self) -> None:
        if self.is_start and self.popen.poll() is None:
            self.popen.kill()

    def get_out(self) -> str:
        if not self.check():
            self.join()
        return self.popen.stdout.read()


@log
def file_head(file_name: str) -> str:
    if not os.path.isfile(file_name):
        return "[red]file not found[/red]"
    with open(file_name, 'r') as fp:
        content = fp.readline()
        if len(content) > 50:
            return content[:50] + "..."
        if len(content) > 0 and content[-1] == '\n':
            return content[:-1]
        return content


@log
def check_empty(check_list: List[str]) -> bool:
    have_err = False
    for name in check_list:
        if not os.path.isfile(name):
            ui.warning(f"'{name}' not found")
            continue
        if os.path.getsize(name) == 0:
            ui.warning(f"'{name}' is empty")
            have_err = True
    return have_err


@log
def execute_pool(
        pool: List[popen],
        max_process: int = -1,
) -> None:
    if max_process == -1:
        with ui.progress() as progress:
            mask = progress.add_task("running...", total=len(pool))
            for i in range(len(pool)):
                ui.detail(f"subprocess {i} start")
                pool[i].start()
                pool[i].join()
                progress.advance(mask)
        return

    with ui.unknown_progress() as progress:
        masks = []
        completed = [False for i in range(len(pool))]
        for i in range(max_process if max_process else len(pool)):
            ui.detail(f"subprocess {i} start")
            masks.append(progress.add_task(f"No.{i+1}", start=False))
            pool[i].start()
        nxt, end_cnt = max_process if max_process else len(pool), 0
        while end_cnt != len(pool):
            time.sleep(0.1)
            for i in range(len(pool)):
                try:
                    if not completed[i] and pool[i].check():
                        # completed this
                        ui.detail(f"subprocess {i} done")
                        end_cnt += 1
                        progress.start_task(masks[i])
                        progress.update(
                            masks[i],
                            completed=100,
                            refresh=True,
                        )
                        completed[i] = True
                        # start next
                        if nxt < len(pool):
                            ui.detail(f"subprocess {nxt} start")
                            masks.append(
                                progress.add_task(f"No.{nxt+1}", start=False))
                            pool[nxt].start()
                            nxt += 1
                except OjpackerError as e:
                    for p in pool:
                        p.halt()
                    ui.error(str(e))
                    raise OjpackerError(
                        f"execute_pool: subprocess {i} get Non-zero exit")
