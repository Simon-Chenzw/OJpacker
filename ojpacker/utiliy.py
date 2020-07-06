from __future__ import absolute_import

import os
import subprocess
import threading
import time
from typing import List

from . import ui


def popen_s2f(cmd: str, input_str: str, output_name: str) -> None:
    """
    get str input, and set output to file
    """
    ui.debug(f"popen_s2f '{cmd}' '{input_str[:-1]}' '{output_name}'")
    with open(output_name, 'w') as file_out:
        popen = subprocess.Popen(cmd.split(),
                                 stdin=subprocess.PIPE,
                                 stdout=file_out,
                                 universal_newlines=True)
        popen.stdin.write(input_str)
        popen.stdin.close()
        popen.wait()


def popen_f2f(cmd: str, input_name: str, output_name: str) -> None:
    """
    get input from file, and set output to file
    """
    ui.debug(f"popen_f2f '{cmd}' '{input_name}' '{output_name}'")
    with open(input_name, 'r') as file_in:
        with open(output_name, 'w') as file_out:
            popen = subprocess.Popen(cmd.split(),
                                     stdin=file_in,
                                     stdout=file_out,
                                     universal_newlines=True)
            popen.wait()


def popen_s2s(cmd: str, input_str: str = "") -> str:
    """
    get str input, and return popen.stdout.read() + popen.stderr.read()
    """
    ui.debug(f"popen_s2s '{cmd}' '{input_str[:-1]}'")
    popen = subprocess.Popen(cmd.split(),
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=True)
    popen.stdin.write(input_str)
    popen.stdin.close()
    popen.wait()
    return popen.stdout.read() + popen.stderr.read()


def file_head(file_name: str) -> str:
    ui.debug(f"get file head of '{file_name}'")
    if not os.path.isfile(file_name):
        return "[red]file not found[/red]"
    with open(file_name, 'r') as fp:
        content = fp.readline()
        if len(content) > 50:
            return content[:50] + "..."
        if len(content) > 0 and content[-1] == '\n':
            return content[:-1]
        return content


def check_empty(check_list: List[str]) -> bool:
    ui.debug("check empty:", check_list)
    have_err = False
    for name in check_list:
        if not os.path.isfile(name):
            ui.warning(f"after making input, '{name}' not found")
            continue
        if os.path.getsize(name) == 0:
            ui.warning(f"'{name}' is empty")
            have_err = True
    return have_err


def exec_thread_pool(thread_pool: List[threading.Thread],
                     multi_thread: bool = False) -> None:
    ui.debug(f"exec_thread_pool, multi_thread: {multi_thread}")
    if not multi_thread:
        with ui.progress() as progress:
            mask = progress.add_task("running...", total=len(thread_pool))
            for thread in thread_pool:
                thread.start()
                thread.join()
                progress.advance(mask)
    else:
        with ui.unknown_progress() as progress:
            masks = [
                progress.add_task(f"No.{i+1}", start=False)
                for i in range(len(thread_pool))
            ]
            completed = [False for i in range(len(thread_pool))]
            for i in range(len(thread_pool)):
                thread_pool[i].start()
            end_cnt = 0
            while end_cnt != len(thread_pool):
                time.sleep(0.2)
                end_cnt = 0
                for i in range(len(thread_pool)):
                    if not thread_pool[i].is_alive():
                        end_cnt += 1
                        if not completed[i]:
                            progress.start_task(masks[i])
                            progress.update(
                                masks[i],
                                completed=100,
                                refresh=True,
                            )
                            completed[i] = True
