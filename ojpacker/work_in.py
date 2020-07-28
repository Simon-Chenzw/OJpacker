from __future__ import absolute_import

import os

from . import config, filetype, ui, utiliy
from .error import OjpackerError
from .ui import log


@log
def precheck() -> None:
    if config.input_exec is not None:
        if not os.path.isfile(config.input_exec.src):
            raise OjpackerError(
                f"input exec '{config.input_exec.src}' not found")
        if config.input_exec.execute_cmd == "":
            raise OjpackerError(
                f"'{config.input_exec.src}' don't have execute command")
        if not os.path.isfile(config.state_name):
            raise OjpackerError(f"state file '{config.state_name}' not found")
        if "{num}" not in config.input_data_name:
            ui.warning("'input_data_name' don't have macro {num}")


@log
def run() -> None:
    if config.input_exec is None:
        ui.info("skip the input phase")
        return
    state = filetype.state_file(config.state_name)
    input_data = filetype.data_file(config.input_data_name)
    length = len(state)
    # make input data
    ui.info(f"running {config.input_exec.exe}")
    pool = [
        utiliy.popen(
            config.input_exec.get_execute(exe_dir="temp"),
            typ="s2f",
            input=state[i],
            output=input_data.with_path(i),
        ) for i in range(length) if len(state[i].split()) != 0
    ]
    utiliy.execute_pool(pool, config.max_process)

    # check empty
    utiliy.check_empty([input_data.with_path(i) for i in range(length)])

    # print input
    if config.show_input:
        detail = [
            "   {name} : {content}".format(
                name="[purple]{:<10}[/purple]".format(input_data[i]),
                content=utiliy.file_head(input_data.with_path(i)),
            ) for i in range(length)
        ]
        for line in detail:
            ui.rprint(line)
        ui.rprint("-----Press enter to continue-----", end="")
        input()
