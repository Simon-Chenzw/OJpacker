from __future__ import absolute_import

import os
import shutil
import threading
import time
from typing import List

from . import filetype, ui, utiliy

garbage: List[str] = []


def work(
        #file
        zip_name: str = None,
        state_name: str = None,
        input_data_name: str = None,
        output_data_name: str = None,
        input_exec: filetype.execfile = None,
        output_exec: filetype.execfile = None,
        input_dir: str = "temp",
        #setting
        show_input: bool = False,
        show_output: bool = False,
        zip_list: List[str] = [],
        executive_part: List[str] = ["in", "out", "zip"],
        multi_thread: bool = False,
) -> None:
    """
    main function of workflow
    """

    mkdir_temp()

    # compile
    if "in" in executive_part:
        compile(input_exec)
    if "out" in executive_part:
        compile(output_exec)

    # input part
    if "in" in executive_part:
        make_input(
            state_name,
            input_data_name,
            input_exec,
            show_input,
            multi_thread,
        )

    # output part
    if "out" in executive_part:
        make_output(
            input_dir,
            input_data_name,
            output_data_name,
            output_exec,
            show_output,
            multi_thread,
        )

    # zip part
    clean(clean_dir=False)
    if "zip" in executive_part:
        zipped(zip_name, zip_list)
        clean(clean_dir=True)


def mkdir_temp() -> None:
    # mkdir
    if os.path.isdir("temp"):
        ui.warning(
            "'temp' already exists, will be [red]deleted[/red] after [blue]10s[/blue]"
        )
        time.sleep(10)
        ui.info("remove directory 'temp'")
        shutil.rmtree("temp")
    ui.info("create directory 'temp'")
    os.mkdir("temp")


def compile(file: filetype.execfile) -> None:

    if file.compile_cmd == None:
        ui.info(f"{file.src} don't have compile command")
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
        ui.error(f"compilation failed, {exe_path} not found")
    else:
        if message:
            ui.debug(
                "-----compile message-----\n",
                message,
                "\n         -----compile message-----",
            )
        garbage.append(exe_path)


def make_input(
        state_name: str,
        input_data_name: str,
        input_exec: filetype.execfile,
        show: bool = False,
        multi_thread: bool = False,
) -> None:
    ui.info("making input")
    ui.info("read state")
    with open(state_name, "r") as state_file:
        state = state_file.readlines()
    ui.info(f"{len(state)} line(s) in state")
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
    ui.debug("check empty of input")
    utiliy.check_empty([
        os.path.join("temp", input_data_name.format(num=i + 1))
        for i in range(len(state))
    ])

    # print input
    if show:
        ui.debug("show input")
        for i in range(len(state)):
            ui.rprint(
                "%2d:" % (i + 1),
                utiliy.file_head(
                    os.path.join("temp", input_data_name.format(num=i + 1))))
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
    ui.info("making output")
    i = 0
    thread_pool = []
    while os.path.isfile(
            os.path.join(input_dir, input_data_name.format(num=i + 1))):
        thread_pool.append(
            threading.Thread(
                target=utiliy.popen_f2f,
                args=(output_exec.get_execute(exe_dir="temp"),
                      os.path.join("temp", input_data_name.format(num=i + 1)),
                      os.path.join("temp",
                                   output_data_name.format(num=i + 1)))))
        i += 1
    ui.info(f"get {len(thread_pool)} input")
    utiliy.exec_thread_pool(thread_pool, multi_thread)

    #check empty
    ui.debug("check empty of output")
    utiliy.check_empty([
        os.path.join("temp", output_data_name.format(num=i + 1))
        for i in range(len(thread_pool))
    ])

    #print output
    if show:
        ui.debug("show output")
        for i in range(len(thread_pool)):
            ui.rprint(
                "%2d:" % (i + 1),
                utiliy.file_head(
                    os.path.join("temp", output_data_name.format(num=i + 1))))
        ui.rprint("-----Press enter to continue-----", end="")
        input()


def zipped(
        zip_name: str,
        zip_list: List[str],
) -> None:
    def readable_byte(value: int) -> str:
        unit = ["B", "KB", "MB", "GB"]
        level = 0
        while (value >= 1024):
            value /= 1024
            level += 1
        return "%.2f %s" % (value, unit[level])

    if zip_list:
        ui.info(f"copy {zip_list} to temporary directory")
        for file_name in zip_list:
            shutil.copyfile(file_name, os.path.join("temp", file_name))
    if os.path.isfile(zip_name + ".zip"):
        ui.warning(f"already have {zip_name}.zip, remove in 10s")
        time.sleep(10)
        os.remove(zip_name + ".zip")
    ui.info("compressing")
    shutil.make_archive(base_name=zip_name, format="zip", root_dir="temp")
    zip_size = readable_byte(os.path.getsize(zip_name + ".zip"))
    ui.info(f"compression complete: '{zip_name}.zip' {zip_size}")


def clean(clean_dir: bool) -> None:
    if clean_dir:
        ui.info("clean up the entire temporary directory")
        shutil.rmtree("temp")
    else:
        ui.info("clean garbage")
        for file_name in garbage:
            ui.debug(f"remove {file_name}")
            os.remove(file_name)
        garbage.clear()
