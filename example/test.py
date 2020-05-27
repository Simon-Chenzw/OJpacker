import os
import sys
sys.path.append("../")
import ojpacker

work = ojpacker.packer(zip_name="problem_data")
state = ojpacker.statefile("state")
input_file = ojpacker.datafile("data{num}.in")
output_file = ojpacker.datafile("data{num}.out")
input_exec = ojpacker.py3file("make_in.py")
output_exec = ojpacker.cppfile("make_out.cpp")
work.load_file(state, input_file, output_file, input_exec, output_exec)
work.load_setting(showoutput=True,
                  zip_list=[output_exec.src],
                  multi_thread=True)
work.work()

#clean garbage
os.remove("problem_data.zip")