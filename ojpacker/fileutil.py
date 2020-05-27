from __future__ import absolute_import
import os
import subprocess
from . import tool
from . import filetype


def popen(cmd, input_type, input_str, output_type, output_str):
    if input_type == "file":
        file_input = open(input_str, 'r')
    elif input_type == "str":
        file_input = subprocess.PIPE
    if output_type == "file":
        file_output = open(output_str, 'w')
    elif output_type == "str":
        file_output = subprocess.PIPE
    popen = subprocess.Popen(cmd.split(),
                             stdin=file_input,
                             stdout=file_output,
                             universal_newlines=True)
    if input_type == "str":
        popen.stdin.write(input_str)
        popen.stdin.close()
    popen.wait()
    if input_type == "file":
        file_input.close()
    if output_type == "file":
        file_output.close()


def popen_exec(cmd):
    """
    no input, and return popen.stdout.read() + popen.stderr.read()
    """
    popen = subprocess.Popen(cmd.split(),
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=True)
    popen.wait()
    return popen.stdout.read() + popen.stderr.read()


def file_head(file_name):
    with open(file_name, 'r') as fp:
        file_content = fp.readline()
        if len(file_content) > 50:
            return file_content[:50] + "..."
        if len(file_content) > 0 and file_content[-1] == '\n':
            return file_content[:-1]
        return file_content


def check_empty(check_list):
    have_err = False
    for file_name in check_list:
        if os.path.getsize(file_name) == 0:
            print(tool.color("purple", file_name + " is empty"))
            have_err = True
    if have_err:
        input(tool.color("yellow", "-----存在空文件---按回车继续-----"))


def compile(execfile, garbage):
    def global_compile(execfile):
        print(f"编译 {execfile.src}")
        message = popen_exec(execfile.compile())
        print("-----编译信息-----")
        print(message)
        garbage.append(execfile.exe)

    def cpp_compile(execfile):
        print(f"编译 {execfile.src}")
        message = popen_exec(execfile.compile())
        # if message.count("error") != 0:
        print("%5d error" % message.count("error"))
        # if message.count("warning") != 0:
        print("%5d warning" % message.count("warning"))
        if message.count("error") > 0:
            print(tool.color("red", "-----编译错误-----"))
            print(message)
            exit()
        garbage.append(execfile.exe)

    file_split = os.path.splitext(execfile.src)
    if len(file_split) > 1 and file_split[1] == ".cpp":
        cpp_compile(execfile)
    elif execfile.compile_cmd is not None:
        global_compile(execfile)