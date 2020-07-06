from __future__ import absolute_import

setting = """
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

make_in = """
import random
import time

time.sleep(random.random())
n = int(input())
print(random.randint(1, n), random.randint(1, n))
"""

make_out = """
#include <iostream>
using namespace std;
int main() {
    int a, b;
    cin >> a >> b;
    cout << a + b;
}
"""

state = """
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


def write(file: str, content: str) -> None:
    with open(file, "w") as fp:
        fp.write(content)


def make_demo() -> None:
    write("ojpacker.json", setting)
    write("state", state)
    write("make_in.py", make_in)
    write("make_out.cpp", make_out)
