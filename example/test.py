import os
import sys
sys.path.append("../")
import ojpacker

input_exec = ojpacker.execfile("make_in.py", execute_cmd="python3 {src}")
output_exec = ojpacker.execfile("make_out.cpp",
                                "make_out.exe",
                                compile_cmd="g++ {src} -o {exe}",
                                execute_cmd="./{exe}")

ojpacker.set_log_level("info")

ojpacker.work(
    zip_name="problem_data",
    state_name="state",
    input_data_name="data{num}.in",
    output_data_name="data{num}.out",
    input_exec=input_exec,
    output_exec=output_exec,
    show_input=True,
    show_output=True,
    zip_list=["state", "make_in.py"],
    multi_thread=True,
)

#clean garbage
os.remove("problem_data.zip")
