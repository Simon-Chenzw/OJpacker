from __future__ import absolute_import

import os
from typing import List

from . import config, filetype, ui, utiliy
from .error import OjpackerError
from .ui import log


@log
def precheck() -> None:
    if config.output_exec is not None:
        if not os.path.isfile(config.output_exec.src):
            raise OjpackerError(
                f"output exec '{config.output_exec.src}' not found")
        if config.output_exec.execute_cmd == "":
            raise OjpackerError(
                f"'{config.output_exec.src}' don't have execute command")
        if config.input_dir != "temp":
            if not os.path.isdir(config.input_dir):
                raise OjpackerError(
                    f"input directory '{config.input_dir}' does not exist")
            elif not os.path.isfile(config.output_data_name.format(num=1)):
                raise OjpackerError(
                    f"Unable to match '{config.output_data_name}' in directory '{config.input_dir}'"
                )
        if "{num}" not in config.input_data_name and config.input_exec is None:
            ui.warning("'input_data_name' don't have macro {num}")
        if "{num}" not in config.output_data_name:
            ui.warning("'output_data_name' don't have macro {num}")


@log
def run() -> None:
    if config.output_exec is None:
        ui.info("skip the output stage")
        return
    input_data = filetype.data_file(config.input_data_name,
                                    path=config.input_dir)
    output_data = filetype.data_file(config.output_data_name)
    # make output data
    length = 0
    pool: List[utiliy.popen] = []
    while os.path.isfile(input_data.with_path(length)):
        pool.append(
            utiliy.popen(
                config.output_exec.get_execute(exe_dir="temp"),
                typ="f2f",
                input=input_data.with_path(length),
                output=output_data.with_path(length),
            ))
        length += 1
    ui.info(f"{length} inputs file detected")
    ui.info(f"running {config.output_exec.exe}")
    utiliy.execute_pool(pool, config.max_process)

    #check empty
    utiliy.check_empty([output_data.with_path(i) for i in range(length)])

    #print output
    if config.show_output:
        detail = [
            "   {name} : {content}".format(
                name="[purple]{:<10}[/purple]".format(output_data[i]),
                content=utiliy.file_head(output_data.with_path(i)),
            ) for i in range(length)
        ]
        for line in detail:
            ui.rprint(line)
        ui.rprint("-----Press enter to continue-----", end="")
        input()
