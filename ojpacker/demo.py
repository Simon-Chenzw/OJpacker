from __future__ import absolute_import

import os

from . import config, ui
from .error import OjpackerError

setting = """\
{
    "defalut_zip_name": "problem_data",
    "state_name": "state",
    "input_data_name": "data{num}.in",
    "output_data_name": "data{num}.out",
    "input_default_exec": "py",
    "output_default_exec": "cpp",
    "input_exec": {
        "cpp": {
            "src": "make_in.cpp",
            "exe": "make_in.out",
            "compile_cmd": "g++ {src} -o {exe}",
            "execute_cmd": "./{exe}"
        },
        "py": {
            "src": "make_in.py",
            "execute_cmd": "python3 {src}"
        }
    },
    "output_exec": {
        "cpp": {
            "src": "make_out.cpp",
            "exe": "make_out.out",
            "compile_cmd": "g++ {src} -o {exe}",
            "execute_cmd": "./{exe}"
        },
        "py": {
            "src": "make_out.py",
            "execute_cmd": "python3 {src}"
        }
    }
}
"""

make_in = """\
import random
import time

time.sleep(random.random())
n = int(input())
print(random.randint(1, n), random.randint(1, n))
"""

make_out = """\
#include <iostream>
using namespace std;
int main() {
    int a, b;
    cin >> a >> b;
    cout << a + b;
}
"""

state = """\
10
10
10
10
100
100
100
100
100
100
"""

content_map = {
    config.json_name: setting,
    "state": state,
    "make_in.py": make_in,
    "make_out.cpp": make_out,
}


def make_demo(dir: str) -> None:
    if os.path.isfile(dir):
        raise OjpackerError(f"there is already a file named {dir}")
    if not os.path.isdir(dir):
        ui.debug(f"make dir {dir}")
        os.mkdir(dir)

    ui.info(f"make demo at {dir}")
    dir = os.path.abspath(dir)
    for file in content_map:
        with open(os.path.join(dir, file), "w") as fp:
            fp.write(content_map[file])
    ui.info(f"you can try to run 'ojpacker' in {dir}")
    ui.info("Confirm that the [cyan]C++[/cyan] compilation command is 'g++'\n")
    ui.info(
        "Confirm that the [cyan]python[/cyan] execution command is 'python3'\n"
    )
    ui.info(
        f"If [red]not[/red], please change the setting in [purple]{config.json_name}[/purple]"
    )
    ui.info(
        "If you want to use other languages, please add relevant settings in json by yourself"
    )


def make_config() -> None:
    if os.path.isfile(config.json_name):
        ui.warning(f"already have '{config.json_name}', will be replaced")
        ui.countdown(5)
    with open(config.json_name, "w") as fp:
        fp.write(setting)
    ui.info(f"'{config.json_name}' created")
    ui.info("Confirm that the [cyan]C++[/cyan] compilation command is 'g++'\n")
    ui.info(
        "Confirm that the [cyan]python[/cyan] execution command is 'python3'\n"
    )
    ui.info(
        f"If [red]not[/red], please change the setting in [purple]{config.json_name}[/purple]"
    )
    ui.info(
        "If you want to use other languages, please add relevant settings in json by yourself"
    )
