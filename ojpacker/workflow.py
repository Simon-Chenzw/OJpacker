from __future__ import absolute_import

import os
import shutil

from . import config, garbage, ui, work_compile, work_in, work_out, work_zip
from .ui import log


@log
def work() -> None:
    """
    main function of workflow
    """
    precheck()
    run()


@log
def precheck() -> None:
    if (config.input_exec is None) and (config.output_exec is None):
        ui.warning("both input phase and output phase will be skipped")
    elif (config.input_exec is None) and config.input_dir == "temp":
        ui.warning("skip input phase and fetch output phase data from 'temp'")
    work_compile.precheck()
    work_in.precheck()
    work_out.precheck()
    work_zip.precheck()


@log
def run() -> None:
    mkdir_temp()
    work_compile.run()
    work_in.run()
    work_out.run()
    garbage.clean()
    work_zip.run()
    garbage.clean(clean_dir=True)


@log
def mkdir_temp() -> None:
    # mkdir
    if config.input_exec is not None:
        if os.path.isdir("temp"):
            ui.warning("'temp' already exists, [red]deleted[/red]")
            shutil.rmtree("temp")
        os.mkdir("temp")
