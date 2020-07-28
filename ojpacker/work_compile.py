from __future__ import absolute_import

import os

from . import config, filetype, garbage, ui, utiliy
from .error import OjpackerError
from .ui import log


@log
def precheck() -> None:
    pass


@log
def run() -> None:
    if config.input_exec is not None:
        compile(config.input_exec)
    if config.output_exec is not None:
        compile(config.output_exec)


@log
def compile(file: filetype.execfile) -> None:

    if not file.compile_cmd:
        ui.detail(f"{file.src} don't have compile command, skip compile")
        return

    ui.info(f"compile {file.src} to {file.exe}")
    message = utiliy.popen(
        file.get_compile(exe_dir="temp"),
        typ="s2s",
        check_return=False,
    ).get_out()
    exe_path = os.path.join("temp", file.exe)
    ui.detail(f"check {exe_path}, {os.path.isfile(exe_path)}")
    if os.path.isfile(exe_path):
        if message:
            if ui.log_level <= ui.level_table["debug"]:
                ui.console.print("[green]-----compile message-----")
                ui.console.print(message)
                ui.console.print("[green]-----compile message-----")
        else:
            ui.detail("no compile message")
        garbage.add(exe_path)
    else:
        if message:
            if ui.log_level <= ui.level_table["warning"]:
                ui.console.print("[yellow]-----compile message-----")
                utiliy.popen(
                    file.get_compile(exe_dir="temp"),
                    capture_output=False,
                    typ="s2s",
                    check_return=False,
                ).join()
                ui.console.print("[yellow]-----compile message-----")
        else:
            ui.warning("no compile message")
        raise OjpackerError(f"compilation failed, {exe_path} not found")
