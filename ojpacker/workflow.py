from __future__ import absolute_import

import os
import shutil
import threading
from typing import List, Optional

from ojpacker.error import OjpackerError

from . import filetype, ui, utiliy

garbage: List[str] = []


def work(
        #file
        zip_name: str = "",
        state_name: str = "",
        input_data_name: str = "",
        output_data_name: str = "",
        input_exec: Optional[filetype.execfile] = None,
        output_exec: Optional[filetype.execfile] = None,
        input_dir: str = "temp",
        #setting
        show_input: bool = False,
        show_output: bool = False,
        zip: bool = False,
        zip_list: List[str] = [],
        multi_thread: bool = False,
) -> None:
    """
    main function of workflow
    """

    # Pre-check
    if input_exec is not None:
        if not os.path.isfile(input_exec.src):
            raise OjpackerError(f"input exec '{input_exec.src}' not found")
        if input_exec.execute_cmd == "":
            raise OjpackerError(
                f"'{input_exec.src}' don't have execute command")
        if not os.path.isfile(state_name):
            raise OjpackerError(f"state file '{state_name}' not found")
        if "{num}" not in input_data_name:
            ui.warning("'input_data_name' don't have macro {num}")
    if output_exec is not None:
        if not os.path.isfile(output_exec.src):
            raise OjpackerError(f"output exec '{output_exec.src}' not found")
        if output_exec.execute_cmd == "":
            raise OjpackerError(
                f"'{output_exec.src}' don't have execute command")
        if input_dir != "temp":
            if not os.path.isdir(input_dir):
                raise OjpackerError(
                    f"input directory '{input_dir}' does not exist")
            elif not os.path.isfile(output_data_name.format(num=1)):
                raise OjpackerError(
                    f"Unable to match '{output_data_name}' in directory '{input_dir}'"
                )
        if "{num}" not in input_data_name and input_exec is None:
            ui.warning("'input_data_name' don't have macro {num}")
        if "{num}" not in output_data_name:
            ui.warning("'output_data_name' don't have macro {num}")
    if (input_exec is None) and (output_exec is None):
        ui.warning("both input phase and output phase will be skipped")
    if zip:
        if zip_name == "":
            raise OjpackerError("zip name is empty")
        for file in zip_list:
            if not os.path.isfile(file):
                ui.warning(f"'{file}' in zip_list, does not exist")
    else:
        if zip_list:
            ui.warning("program won't make zip, but zip_list is not empty")

    if input_exec is None and input_dir == "temp":
        ui.warning("skip input phase and fetch output phase data from 'temp'")
    else:
        mkdir_temp()

    # compile
    if input_exec is not None:
        compile(input_exec)
    if output_exec is not None:
        compile(output_exec)

    # input part
    if input_exec is not None:
        ui.debug("input phase start")
        make_input(
            state_name,
            input_data_name,
            input_exec,
            show_input,
            multi_thread,
        )
    else:
        ui.info("skip the input phase")

    # output part
    if output_exec is not None:
        ui.debug("output phase start")
        make_output(
            input_dir,
            input_data_name,
            output_data_name,
            output_exec,
            show_output,
            multi_thread,
        )
    else:
        ui.info("skip the output stage")

    # zip part
    clean(clean_dir=False)
    if zip:
        zipped(zip_name, zip_list)
        clean(clean_dir=True)
    else:
        ui.info("data has been stored in temporary directory")


def mkdir_temp() -> None:
    # mkdir
    if os.path.isdir("temp"):
        ui.warning(
            "'temp' already exists, will be [red]deleted[/red] after [blue]10s[/blue]"
        )
        ui.countdown(10)
        ui.debug("remove directory 'temp'")
        shutil.rmtree("temp")
    ui.debug("create directory 'temp'")
    os.mkdir("temp")


def compile(file: filetype.execfile) -> None:

    if not file.compile_cmd:
        ui.debug(f"{file.src} don't have compile command, skip compile")
        return

    ui.info(f"compile {file.src} to {file.exe}")
    message = utiliy.popen_s2s(file.get_compile(exe_dir="temp"))
    exe_path = os.path.join("temp", file.exe)
    ui.debug(f"check {exe_path}, {os.path.isfile(exe_path)}")
    if not os.path.isfile(exe_path):
        ui.warning(
            "-----compile message-----\n",
            message,
            "\n         -----compile message-----",
        )
        raise OjpackerError(f"compilation failed, {exe_path} not found")
    else:
        if message:
            ui.debug(
                "-----compile message-----\n",
                message,
                "\n         -----compile message-----",
            )
        ui.debug(f"add {exe_path} to garbage")
        garbage.append(exe_path)


def make_input(
        state_name: str,
        input_data_name: str,
        input_exec: filetype.execfile,
        show: bool = False,
        multi_thread: bool = False,
) -> None:
    ui.debug("read state")
    with open(state_name, "r") as state_file:
        state = state_file.readlines()
    if len(state) != 0:
        ui.info(f"{len(state)} line(s) in state")
    else:
        raise OjpackerError("state file is empty")
    # make input data
    thread_pool = [
        threading.Thread(target=utiliy.popen_s2f,
                         args=(input_exec.get_execute(exe_dir="temp"),
                               state[i],
                               os.path.join(
                                   "temp",
                                   input_data_name.format(num=i + 1),
                               ))) for i in range(len(state))
        if len(state[i].split()) != 0
    ]
    ui.info(f"running {input_exec.exe}, multithread: {multi_thread}")
    utiliy.exec_thread_pool(thread_pool, multi_thread)

    # check empty
    utiliy.check_empty([
        os.path.join("temp", input_data_name.format(num=i + 1))
        for i in range(len(state))
    ])

    # print input
    if show:
        ui.debug("show input")
        detail = [
            "   {name} : {content}".format(
                name="[purple]" +
                "{:<10}".format(input_data_name.format(num=i + 1)) +
                "[/purple]",
                content=utiliy.file_head(
                    os.path.join("temp", input_data_name.format(num=i + 1))),
            ) for i in range(len(state))
        ]
        for line in detail:
            ui.rprint(line)
        ui.rprint("-----Press enter to continue-----", end="")
        input()


def make_output(
        input_dir: str,
        input_data_name: str,
        output_data_name: str,
        output_exec: filetype.execfile,
        show: bool,
        multi_thread: bool,
) -> None:

    # make output data
    i = 0
    thread_pool = []
    while os.path.isfile(
            os.path.join(input_dir, input_data_name.format(num=i + 1))):
        thread_pool.append(
            threading.Thread(
                target=utiliy.popen_f2f,
                args=(output_exec.get_execute(exe_dir="temp"),
                      os.path.join(input_dir,
                                   input_data_name.format(num=i + 1)),
                      os.path.join("temp",
                                   output_data_name.format(num=i + 1)))))
        i += 1
    ui.info(f"{len(thread_pool)} inputs file detected")
    utiliy.exec_thread_pool(thread_pool, multi_thread)

    #check empty
    utiliy.check_empty([
        os.path.join("temp", output_data_name.format(num=i + 1))
        for i in range(len(thread_pool))
    ])

    #print output
    if show:
        ui.debug("show output")
        detail = [
            "   {name} : {content}".format(
                name="[purple]" +
                "{:<10}".format(output_data_name.format(num=i + 1)) +
                "[/purple]",
                content=utiliy.file_head(
                    os.path.join("temp", output_data_name.format(num=i + 1))),
            ) for i in range(len(thread_pool))
        ]
        for line in detail:
            ui.rprint(line)
        ui.rprint("-----Press enter to continue-----", end="")


def zipped(
        zip_name: str,
        zip_list: List[str],
) -> None:
    def readable_byte(value: float) -> str:
        unit = ["B", "KB", "MB", "GB"]
        level = 0
        while (value >= 1024):
            value /= 1024
            level += 1
        return "%.2f %s" % (value, unit[level])

    if zip_list:
        ui.info("copy file in 'zip_list' to temporary directory")
        for file_name in zip_list:
            if not os.path.isfile(file_name):
                ui.warning(f"in 'zip_list', {file_name} not found")
                continue
            shutil.copyfile(file_name, os.path.join("temp", file_name))
    if os.path.isfile(zip_name + ".zip"):
        ui.warning(f"already have {zip_name}.zip, remove in 10s")
        ui.countdown(10)
        ui.info(f"remove old {zip_name}.zip")
        os.remove(zip_name + ".zip")
    ui.info("start compression")
    shutil.make_archive(base_name=zip_name, format="zip", root_dir="temp")
    zip_size = readable_byte(os.path.getsize(zip_name + ".zip"))
    ui.info(f"compression complete: '{zip_name}.zip' {zip_size}")


def clean(clean_dir: bool) -> None:
    if clean_dir:
        ui.debug("clean up the entire temporary directory")
        shutil.rmtree("temp")
    else:
        ui.debug("clean garbage", garbage)
        for file_name in garbage:
            if not os.path.isfile(file_name):
                ui.warning(f"garbage '{file_name}' not found")
                continue
            os.remove(file_name)
        garbage.clear()
