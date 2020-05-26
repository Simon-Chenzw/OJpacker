import sys
sys.path.append("../")
import ojpacker

work = ojpacker.packer()
state = ojpacker.statefile()
input_file = ojpacker.datafile("data{num}.in")
output_file = ojpacker.datafile("data{num}.out")
input_exec = ojpacker.execfile("make_in.py", execute_cmd="python3 {src}")
output_exec = ojpacker.execfile("make_out.cpp", "make_out.out",
                                "g++ {src} -o {exe}", "./{exe}")
work.load_file(state, input_file, output_file, input_exec, output_exec)
work.load_setting(showoutput=True,
                  zip_list=[input_exec.src],
                  multi_thread=False)
work.work()