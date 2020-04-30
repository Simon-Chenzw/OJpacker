#!/usr/bin/python3

import threading
import traceback
import time
import sys
import os


class config:
    states = []

    #名字相关参数
    problem_name = "problem_data"
    states_name = "states"
    input_exec_name_list = {"python3": "make.py", "c++": "make.cpp"}
    output_exec_name_list = {"c++": "std.cpp"}

    #流程参数
    input_exec_type = "python3"
    input_edit = False
    input_edit_num = 0
    skip_input = False
    output_exec_type = "c++"
    output_print = False
    skip_output = False
    zipped = True
    zipped_input_exec = False
    zipped_output_exec = False
    zipped_states = False
    garbage = []

    def __init__(self):
        self.get_states()

    def input_file(self, num):
        return "data%d.in" % num

    def output_file(self, num):
        return "data%d.out" % num

    def exec(self, file_type, file_name):
        if file_type == "c++":
            return "./" + file_name[:-4] + ".out"
        if file_type == "python3":
            return "python3 " + file_name

    def input_exec(self):
        return self.exec(self.input_exec_type, self.input_exec_name())

    def output_exec(self):
        return self.exec(self.output_exec_type, self.output_exec_name())

    def input_exec_name(self):
        return self.input_exec_name_list[self.input_exec_type]

    def output_exec_name(self):
        return self.output_exec_name_list[self.output_exec_type]

    def get_states(self):
        with open(self.states_name, mode='r') as states_file:
            for line in states_file.read().split('\n'):
                if line != "":
                    self.states.append(line)


def Progress_Bar(output_str, print_cnt=True, is_begin=True):
    if is_begin:
        thread = threading.Thread(target=Progress_Bar,
                                  args=(output_str, print_cnt, False))
        thread.start()
        return thread
    global cnt
    i = 0
    char = ['\\', '|', '/', '—']
    time.sleep(0.1)
    if print_cnt:
        while cnt != -1:
            print("\r%s:%3d %c   " % (output_str, cnt, char[i % 4]), end='')
            i += 1
            time.sleep(0.1)
    else:
        while cnt != -1:
            print("\r%s:   %c   " % (output_str, char[i % 4]), end='')
            i += 1
            time.sleep(0.1)


def guide():
    print("""\
./work.sh [options] problem_name

    options:
        -e edit         after making input it will hang up
                            a number(0~9) can write after this option, and it description 
                            the number of the input files (1,2,...) that will be automatic open in vscode
        -j just_input   same as description just make input
        -d detail       will print the first line of output after making
        -s skip_zip     program won't zip data 
        -icpp           use c++ for input_exec
        -ipy            use python3 for input_exec

            you can change default options at variable "config" in this file
    
    problem_name:
        the name of the zip, and by default will be problem_data

    Requires three types of files:   (located at same directory)
        states          the parameter of each point, each hold one line
        input_exec      get parameter and print input
        output_exec     can get input and print output
        
        name of these files is in this file at these variable:
            config.input_exec_name_list
            config.output_exec_name_list

    during the program it will make a directory called \"temp\", And before exit it will be removed
""")


def analyze_sys_argv():
    global arg
    #参数分析
    if "-h" in sys.argv:
        guide()
        exit()
    skip_next = False
    for i in range(1, len(sys.argv)):
        if skip_next:
            skip_next = False
            continue
        if sys.argv[i] == "-e":
            arg.input_edit = True
            if i < len(sys.argv) - 1 and sys.argv[i + 1] in map(
                    str, range(10)):
                arg.input_edit_num = int(sys.argv[i + 1])
                skip_next = True
        elif sys.argv[i] == "-d":
            arg.output_print = True
        elif sys.argv[i] == "-u":
            arg.zipped = False
        elif sys.argv[i] == "-icpp":
            arg.input_exec_type = "c++"
        elif sys.argv[i] == "-ipy":
            arg.input_exec_type = "python3"
        elif sys.argv[i] == "-zin":
            arg.zipped_input_exec = True
        elif sys.argv[i] == "-zout":
            arg.zipped_output_exec = True
        elif sys.argv[i] == "-zstates":
            arg.zipped_states = True
        elif sys.argv[i] == "-sin":
            arg.skip_input = True
        elif sys.argv[i] == "-sout":
            arg.skip_output = True
        #若要添加自定义参数 请在这添加
        elif sys.argv[i][0] == '-':
            print("参数错误 使用参数-h以获取指南")
            exit()
        else:
            if arg.problem_name == "problem_data":
                arg.problem_name = sys.argv[i]
            else:
                print("题目名过多 使用参数-h以获取指南")
                exit()


def make_temp_dir():
    global arg
    if arg.skip_input:
        return
    if os.path.isdir("temp"):
        os.system("rm -rf temp")
    os.system("mkdir temp")


def pre_compile():
    def cpp_compile(file_name):
        file_head = file_name[:-4]
        print("编译 %s.cpp" % file_head)
        message = os.popen("g++ %s.cpp -o %s.out -std=c++17 -O3 2>&1" %
                           (file_head, file_head)).read()
        if message.count("error") != 0:
            print("%5d error" % message.count("error"))
        if message.count("warning") != 0:
            print("%5d warning" % message.count("warning"))
        if message.count("error") > 0:
            print("\033[0;31m" + "-----编译错误-----" + "\033[0m")
            print(message)
            exit()
        arg.garbage.append(file_head + ".out")

    global arg
    if arg.input_exec_type == "c++":
        cpp_compile(arg.input_exec_name())
    if arg.output_exec_type == "c++":
        cpp_compile(arg.output_exec_name())


def check_empty(check_list):
    have_err = False
    for file_name in check_list:
        get_mess = os.popen("wc -c temp/%s" % file_name).read().split()
        if get_mess[0] == '0':
            print("\033[0;35m" + "%s is empty" % get_mess[-1].split('/')[-1] +
                  "\033[0m")
            have_err = True
    if have_err:
        input("\033[0;33m" + "-----存在空文件---按回车继续-----" + "\033[0m")


def make_input_data():
    global arg
    if arg.skip_input:
        return
    #构造数据
    global cnt
    cnt = 0
    Bar = Progress_Bar("数据生成中")
    for line in arg.states:
        cnt += 1
        os.system("echo %s | %s >temp/%s" %
                  (line, arg.input_exec(), arg.input_file(cnt)))
    cnt = -1
    Bar.join()
    print("\r数据生成完成: %d\033[K" % len(arg.states))
    #编辑input
    if arg.input_edit:
        for i in range(arg.input_edit_num, 0, -1):
            os.system("code temp/%s" % arg.input_file(i))
        input("-----等待更改完成---按回车继续-----")
    check_empty([arg.input_file(i + 1) for i in range(len(arg.states))])


def make_output_data():
    global arg
    if arg.skip_output:
        return
    global cnt
    cnt = 1
    Bar = Progress_Bar("结果生成中")
    while os.path.isfile("temp/%s" % arg.input_file(cnt)):
        os.system(
            "%s < temp/%s > temp/%s" %
            (arg.output_exec(), arg.input_file(cnt), arg.output_file(cnt)))
        cnt += 1
    cnt = -1
    Bar.join()
    print("\r结果生成完成: %d\33[K" % len(arg.states))
    #check empty
    check_empty([arg.output_file(i + 1) for i in range(len(arg.states))])
    #print output
    if arg.output_print:
        cnt = 1
        while os.path.isfile("temp/%s" % arg.input_file(cnt)):
            file_content = os.popen("head -n 1 temp/%s" %
                                    arg.output_file(cnt)).read()
            if len(file_content) > 50:
                file_content = file_content[:50] + "..."
            if len(file_content) > 0 and file_content[-1] == '\n':
                file_content = file_content[:-1]
            print("%2d: %s" % (cnt, file_content))
            cnt += 1
        input("-----显示结果完成---按回车继续-----")


def zipped():
    global arg
    if arg.zipped:
        global cnt
        cnt = 0
        if arg.zipped_input_exec:
            os.system("cp %s temp" % arg.input_exec_name())
        if arg.zipped_output_exec:
            os.system("cp %s temp" % arg.output_exec_name())
        if arg.zipped_states:
            os.system("cp %s temp" % arg.states_name)
        bar = Progress_Bar("打包数据中", print_cnt=False)
        os.system("cd temp && zip -q -m -r ../%s.zip ." % arg.problem_name)
        zip_size = os.popen("ls -lh | grep %s.zip" %
                            arg.problem_name).read().split()[4]
        cnt = -1
        bar.join()
        print("\r打包数据完成:  %s.zip  %s\33[K" % (arg.problem_name, zip_size))
    else:
        print("数据打包命令为:\ncd temp && zip -m -r ../%s.zip ." % arg.problem_name)


def clean(clean_temp_dir=True):
    if clean_temp_dir: os.system("rm -rf temp")
    for file_name in arg.garbage:
        os.system("rm %s" % file_name)


try:
    arg = config()
    analyze_sys_argv()
    make_temp_dir()
    pre_compile()
    make_input_data()
    make_output_data()
    zipped()
    clean()
    print("\033[31m" + "-----完成-----" + "\033[0m")
except KeyboardInterrupt:
    clean(clean_temp_dir=False)
    print()