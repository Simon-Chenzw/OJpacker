#!/usr/bin/python3
# version: v1.1.0

import os
import sys
import time
import json
import requests
import argparse
import traceback
import threading


class file_info:

    config_json = "config.json"
    states = list()
    garbage = list()

    # 其他参数
    # option    namespace
    # json_data dictionary

    def __init__(self):
        # load json
        if not os.path.isfile(self.config_json):
            make_default_json(self.config_json)
        with open(self.config_json, 'r') as json_file:
            self.json_data = json.load(json_file)
        # load arg
        self.option = get_parser(self.json_data).parse_args()
        if self.option.make_default_json:
            make_default_json(self.config_json)
        # check update
        if self.option.install_latest:
            self.option.install_version = "latest"
        if self.option.install_version != "not_upgrade":
            upgrade_script(self, self.option.install_version)
            exit()
        # get states
        self.get_states()

    def get_states(self):
        with open(self.json_data["states_name"], mode='r') as states_file:
            for line in states_file.read().split('\n'):
                if line != "":
                    self.states.append(line)

    def input_file(self, num):
        return self.json_data["input_file_name"] % num

    def output_file(self, num):
        return self.json_data["output_file_name"] % num

    def input_exec_name(self):
        return self.json_data["input_exec_name_list"][
            self.option.input_exec_type]

    def output_exec_name(self):
        return self.json_data["output_exec_name_list"][
            self.option.output_exec_type]

    def exec(self, file_type, file_name):
        if file_type == "py":
            return "python3 " + file_name
        if file_type == "cpp":
            return f"./{file_name[:-4]}.out"

    def input_exec(self):
        return self.exec(self.option.input_exec_type, self.input_exec_name())

    def output_exec(self):
        return self.exec(self.option.output_exec_type, self.output_exec_name())


def get_parser(json_data):
    # guide https://docs.python.org/3/library/argparse.html
    # help
    parser = argparse.ArgumentParser(
        usage="./" + json_data["script_name"] + " [name] [-option]",
        description="One simple script for making date in OI",
        epilog=
        "you can use the first letter of the optional arguments as abbreviation, if the abbreviation is unambiguous"
    )
    # 压缩包名字
    parser.add_argument("name",
                        nargs='?',
                        default=json_data["default_zip_name"],
                        help="name of the zip")
    # 修改的in文件个数
    edit_help = "pause after make input, previous NUM (default:%(const)s) will open in vscode"
    parser.add_argument("-edit",
                        nargs='?',
                        const=0,
                        default=-1,
                        type=int,
                        help=edit_help,
                        metavar="NUM",
                        dest="input_edit_num")
    # 输出out文件细节
    parser.add_argument("-detail",
                        action='store_true',
                        help="print the detail of all output file",
                        dest="output_print")
    # 构造in的语言类型
    parser.add_argument("-input",
                        default=json_data["default_input_exec_type"],
                        choices=['py', 'cpp'],
                        help="the language that make input",
                        dest="input_exec_type")
    # 构造out的语言类型
    parser.add_argument("-output",
                        default=json_data["default_output_exec_type"],
                        choices=['py', 'cpp'],
                        help="the language that make output",
                        dest="output_exec_type")
    # 需要打包至zip中的文件
    parser.add_argument(
        "-zip",
        nargs='+',
        default=[],
        choices=["in", "out", "states"],
        help="FILE={in,out,states} file(s) put into the zip. " +
        "\"in\" means the code of making input" +
        "\"out\" means the code of making output",
        metavar="FILE",
        dest="zip_file")
    # 需要跳过的流程
    parser.add_argument("-skip",
                        nargs='+',
                        default=[],
                        choices=["in", "out", "zip"],
                        help="STAGE={in,out,zip} skip the stage.",
                        metavar="STAGE",
                        dest="skip")
    # 更新 互斥组
    update_group = parser.add_mutually_exclusive_group()
    # 通过github更新
    update_group.add_argument("-upgrade",
                              action='store_true',
                              help="upgrade to the latest version",
                              dest="install_latest")
    # 通过github安装
    update_group.add_argument("-get",
                              nargs=1,
                              default="not_upgrade",
                              help="get the selected version",
                              metavar="version",
                              dest="install_version")
    # 创建默认json
    parser.add_argument("-make_json",
                        action='store_true',
                        help="make default json file",
                        dest="make_default_json")
    return parser


def upgrade_script(arg, version):
    def download(url):
        requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
        ses = requests.session()
        ses.keep_alive = False  # 关闭多余连接
        try:
            return ses.get(url)
        except:
            print("fail to get from :\n    " + url)
            exit()

    old_version = arg.json_data["version"]
    print("Current version : " + old_version)
    print("Upgrade to : " + version)
    if version == "latest":
        api_url = arg.json_data["github_url"] + "/latest"
    else:
        api_url = arg.json_data["github_url"] + "/tags/" + version
    print("Get " + version + " version description from :\n    " + api_url)
    version_json = download(api_url).json()
    # api 获取失败
    if "message" in version_json:
        print(version_json["message"])
        print("Check the url or the version name")
        return
    # 需要更新至最新版 但已经是最新版
    if version == "latest" and version_json["tag_name"] == old_version:
        print("Already the latest version")
        print("Use \"-get " + old_version + "\" to compulsory upgrade")
        return
    # ignore version
    if version == "latest" and version_json["tag_name"] in arg.json_data[
            "ignore_version"]:
        print("Latest version is \"" + version_json["tag_name"] +
              "\".Is the ignored version")
        return
    print("Successfully get version json, download file")
    for asset in version_json["assets"]:
        download_url = asset["browser_download_url"]
        file_name = asset["name"]
        print("Download " + file_name)
        res = download(download_url)
        if asset["name"] == "data_maker.py":
            asset["name"] = arg.json_data["script_name"]
        with open(file_name, "wb") as fl:
            fl.write(res.content)
    # 更改json 版本
    with open(arg.config_json, 'w') as json_file:
        arg.json_data["version"] = version_json["tag_name"]
        json.dump(arg.json_data, json_file, indent=4)
    print("Successfully get the version: " + version)
    print("Use \"-get " + old_version + "\" to back to old version")
    print("version " + version_json["tag_name"] + " depiction:\n" +
          version_json["body"])


def make_default_json(json_name):
    json_data = {
        'version':
        'v1.0.0',
        'ignore_version': [],
        'default_zip_name':
        'problem_data',
        'default_input_exec_type':
        'py',
        'default_output_exec_type':
        'cpp',
        'script_name':
        'work.py',
        'states_name':
        'states',
        'input_file_name':
        'data%d.in',
        'output_file_name':
        'data%d.out',
        'input_exec_name_list': {
            'py': 'make_in.py',
            'cpp': 'make_in.cpp'
        },
        'output_exec_name_list': {
            'py': 'make_out.py',
            'cpp': 'make_out.cpp'
        },
        'compile_cmd': {
            '_comment':
            'file_head is the name you set in exec_name_list without suffix',
            'cpp': 'g++ {file_head}.cpp -o {file_head}.out -std=c++17 -O3 2>&1'
        },
        'zip_cmd':
        'cd temp && zip -q -m -r ../{zip_name}.zip .',
        'github_url':
        'https://api.github.com/repos/Simon-Chenzw/data_maker/releases'
    }
    with open(json_name, 'w') as json_file:
        json.dump(json_data, json_file, indent=4)
    exit()


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


def make_temp_dir():
    global arg
    if "in" in arg.option.skip:
        return
    if os.path.isdir("temp"):
        os.system("rm -rf temp")
    os.system("mkdir temp")


def pre_compile():
    def cpp_compile(file_name):
        file_head = file_name[:-4]
        print(f"编译 {file_head}.cpp")
        message = os.popen(arg.json_data["compile_cmd"]["cpp"].format(
            file_head=file_head)).read()
        # if message.count("error") != 0:
        print("%5d error" % message.count("error"))
        # if message.count("warning") != 0:
        print("%5d warning" % message.count("warning"))
        if message.count("error") > 0:
            print("\033[0;31m" + "-----编译错误-----" + "\033[0m")
            print(message)
            exit()
        arg.garbage.append(file_head + ".out")

    global arg
    if arg.option.input_exec_type == "cpp":
        cpp_compile(arg.input_exec_name())
    if arg.option.output_exec_type == "cpp":
        cpp_compile(arg.output_exec_name())


def check_empty(check_list):
    have_err = False
    for file_name in check_list:
        get_mess = os.popen(f"wc -c temp/{file_name}").read().split()
        if get_mess[0] == '0':
            print("\033[0;35m" + f"{get_mess[-1].split('/')[-1]} is empty" +
                  "\033[0m")
            have_err = True
    if have_err:
        input("\033[0;33m" + "-----存在空文件---按回车继续-----" + "\033[0m")


def make_input_data():
    global arg
    if "in" in arg.option.skip:
        return
    #构造数据
    global cnt
    cnt = 0
    Bar = Progress_Bar("数据生成中")
    for state in arg.states:
        cnt += 1
        os.system(
            f"echo {state} | {arg.input_exec()} >temp/{arg.input_file(cnt)}")
    cnt = -1
    Bar.join()
    print("\r" + f"数据生成完成: {len(arg.states)}" + "\033[K")
    #编辑input
    if arg.option.input_edit_num >= 0:
        for i in range(arg.option.input_edit_num, 0, -1):
            os.system(f"code temp/{arg.input_file(i)}")
        input("-----等待更改完成---按回车继续-----")
    check_empty([arg.input_file(i + 1) for i in range(len(arg.states))])


def make_output_data():
    global arg
    if "out" in arg.option.skip:
        return
    global cnt
    cnt = 1
    Bar = Progress_Bar("结果生成中")
    while os.path.isfile(f"temp/{arg.input_file(cnt)}"):
        os.system(
            f"{arg.output_exec()} < temp/{arg.input_file(cnt)} > temp/{arg.output_file(cnt)}"
        )
        cnt += 1
    cnt = -1
    Bar.join()
    print("\r" + f"结果生成完成: {len(arg.states)}" + "\33[K")
    #check empty
    check_empty([arg.output_file(i + 1) for i in range(len(arg.states))])
    #print output
    if arg.option.output_print:
        for i in range(1, len(arg.states) + 1):
            file_content = os.popen(
                f"head -n 1 temp/{arg.output_file(i)}").read()
            if len(file_content) > 50:
                file_content = file_content[:50] + "..."
            if len(file_content) > 0 and file_content[-1] == '\n':
                file_content = file_content[:-1]
            print("%2d: %s" % (i, file_content))
        input("-----显示结果完成---按回车继续-----")


def zipped():
    global arg
    if "zip" in arg.option.skip:
        print(arg.json_data["zip_cmd"].format(zip_name=arg.option.name))
        return
    global cnt
    cnt = 0
    if "in_exec" in arg.option.zip_file:
        os.system("cp %s temp" % arg.input_exec_name())
    if "out_exec" in arg.option.zip_file:
        os.system("cp %s temp" % arg.output_exec_name())
    if "states" in arg.option.zip_file:
        os.system("cp %s temp" % arg.json_data["states_name"])
    bar = Progress_Bar("打包数据中", print_cnt=False)
    os.system(arg.json_data["zip_cmd"].format(zip_name=arg.option.name))
    zip_size = os.popen(
        f"ls -lh | grep {arg.option.name}.zip").read().split()[4]
    cnt = -1
    bar.join()
    print("\r" + f"打包数据完成:  {arg.option.name}.zip  {zip_size}" + "\33[K")


def clean(clean_temp_dir=True):
    if clean_temp_dir: os.system("rm -rf temp")
    for file_name in arg.garbage:
        os.system("rm %s" % file_name)


try:
    arg = file_info()
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