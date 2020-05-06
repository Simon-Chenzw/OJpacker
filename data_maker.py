#!/usr/bin/python3

import os
import sys
import stat
import time
import json
import shutil
import platform
import requests
import argparse
import threading
import subprocess

version = 'v1.3.0'


class config:
    # Do not remove the comments below
    # start of default json_data
    json_data = {
        'ignore_version': [],
        'default_zip_name':
        'problem_data',
        'default_input_exec_type':
        'py',
        'default_output_exec_type':
        'cpp',
        'state_name':
        'state',
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
        'exec_cmd': {
            '_comment':
            'file_head is the name you set in exec_name_list without suffix',
            'py': 'python3 {file_head}.py',
            'cpp': './{file_head}.out'
        },
        'zip_cmd':
        'cd temp && zip -q -m -r ../{zip_name}.zip .',
        'github_url':
        'https://api.github.com/repos/Simon-Chenzw/data_maker/releases'
    }

    # end of default json_data

    def __init__(self, json_name="config.json"):
        self.json_name = json_name
        self.load_json()
        # self.script_name = sys.argv[0].split('/')[-1]

    def load_json(self):
        self.default_json_data_str = json.dumps(self.json_data, indent=4)
        try:
            with open(self.json_name, 'r') as json_file:
                self.json_data.update(json.load(json_file))
        except json.decoder.JSONDecodeError:
            print(
                "The json format is wrong, you can use \"-config_dump\" to overwrite config to the default value"
            )
            print("Use default config")
        except FileNotFoundError:
            # print(f"\"{self.json_name}\" not found, use default config")
            if platform.system().lower() == "Windows":
                print(
                    "please use \"-config_dump\" and change \"compile_cmd exec_cmd zip_cmd\" for your platform"
                )
                exit()

    def dump_default_json(self):
        if os.path.isfile(self.json_name):
            if tool.yesorno("Keep old json?"):
                os.rename(self.json_name, "old_" + self.json_name)
                print("Old json has been renamed to \"old_%s\"" %
                      self.json_name)
        with open(self.json_name, 'w') as fp:
            fp.write(self.default_json_data_str)
        print("Default json has been dumped to \"%s\"" % self.json_name)


class argument:
    def __init__(self, args_str=None):
        if args_str == None:
            self.option = self.get_parser().parse_args()
        else:
            self.option = self.get_parser().parse_args(args_str)

    @staticmethod
    def get_parser():
        # guide https://docs.python.org/3/library/argparse.html
        # help
        parser = argparse.ArgumentParser(
            usage=sys.argv[0].split('/')[-1] + " [name] [-option]",
            description="One simple script for making date in OI",
            epilog=
            "you can use the first letter of the optional arguments as abbreviation, if the abbreviation is unambiguous"
        )
        # 跟工作有关的option
        work_option_group = parser.add_argument_group('work option')
        # 压缩包名字
        work_option_group.add_argument("name",
                                       nargs='?',
                                       default="_default_zip_name",
                                       help="name of the zip")
        # 修改的in文件个数
        work_option_group.add_argument(
            "-edit",
            nargs='?',
            const=0,
            default=-1,
            type=int,
            help=
            "pause after make input, previous NUM (default:%(const)s) will open in vscode",
            metavar="NUM",
            dest="input_edit_num")
        # 输出out文件细节
        work_option_group.add_argument(
            "-detail",
            action='store_true',
            help="print the detail of all output file",
            dest="output_print")
        # 构造in的语言类型
        work_option_group.add_argument("-input",
                                       default="_default_input_exec_type",
                                       choices=['py', 'cpp'],
                                       help="the language that make input",
                                       dest="input_exec_type")
        # 构造out的语言类型
        work_option_group.add_argument("-output",
                                       default="_default_output_exec_type",
                                       choices=['py', 'cpp'],
                                       help="the language that make output",
                                       dest="output_exec_type")
        # 需要打包至zip中的文件
        work_option_group.add_argument(
            "-zip",
            nargs='+',
            default=[],
            choices=["in", "out", "state", "extra"],
            help="FILE={in,out,state} file(s) put into the zip. " +
            "\"in\" means the code of making input" +
            "\"out\" means the code of making output",
            metavar="FILE",
            dest="zip_file")
        # 需要跳过的流程
        work_option_group.add_argument(
            "-skip",
            nargs='+',
            default=[],
            choices=["in", "out", "zip"],
            help="STAGE={in,out,zip} skip the stage.",
            metavar="STAGE",
            dest="skip")
        # 脚本本体相关
        script_option_group = parser.add_argument_group('script option')
        # version
        script_option_group.add_argument("-version",
                                         action='store_true',
                                         help="print version",
                                         dest="print_version")
        # 通过github更新
        script_option_group.add_argument("-upgrade",
                                         action='store_true',
                                         help="upgrade to the latest version",
                                         dest="install_latest")
        # 通过github安装
        script_option_group.add_argument("-get",
                                         nargs=1,
                                         default=["not_upgrade"],
                                         help="get the selected version",
                                         metavar="version",
                                         dest="install_version")
        # 默认json相关
        script_option_group.add_argument("-json_dump",
                                         action='store_true',
                                         help="make default json file",
                                         dest="json_dump_default")
        return parser


class explainer(config, argument):
    zip_list = list()

    def __init__(self, json_name="config.json", args_str=None):
        config.__init__(self, json_name)
        argument.__init__(self, args_str)
        self.analyze_scipt_option()
        self.add_zip_list()

    def add_zip_list(self):
        if "in" in self.option.zip_file:
            self.zip_list.append(self.input_exec_name())
        if "out" in self.option.zip_file:
            self.zip_list.append(self.output_exec_name())
        if "state" in self.option.zip_file:
            self.zip_list.append(self.json_data["state_name"])
        if "extra" in self.option.zip_file:
            self.zip_list += input("input extra zip file list:").split()

    def analyze_scipt_option(self):
        if self.option.install_latest:
            tool.download_version(self.json_data["github_url"], "latest",
                                  self.json_data["ignore_version"])
            exit()
        if self.option.install_version[0] != "not_upgrade":
            tool.download_version(self.json_data["github_url"],
                                  self.option.install_version[0],
                                  self.json_data["ignore_version"])
            exit()
        if self.option.json_dump_default:
            self.dump_default_json()
            exit()
        if self.option.print_version:
            print("Version :", version)
            exit()

    def zip_name(self):
        if self.option.name != "_default_zip_name":
            return self.option.name
        else:
            return self.json_data["default_zip_name"]

    def input_name(self, num):
        return self.json_data["input_file_name"] % num

    def output_name(self, num):
        return self.json_data["output_file_name"] % num

    def input_exec_type(self):
        if self.option.input_exec_type != "_default_input_exec_type":
            return self.option.input_exec_type
        else:
            return self.json_data["default_input_exec_type"]

    def output_exec_type(self):
        if self.option.output_exec_type != "_default_output_exec_type":
            return self.option.output_exec_type
        else:
            return self.json_data["default_output_exec_type"]

    def input_exec_name(self):
        return self.json_data["input_exec_name_list"][self.input_exec_type()]

    def output_exec_name(self):
        return self.json_data["output_exec_name_list"][self.output_exec_type()]

    def exec_cmd(self, file_type, file_name):
        return self.json_data["exec_cmd"][file_type].format(
            file_head=os.path.splitext(file_name)[0])

    def input_exec_cmd(self):
        return self.exec_cmd(self.input_exec_type(), self.input_exec_name())

    def output_exec_cmd(self):
        return self.exec_cmd(self.output_exec_type(), self.output_exec_name())


class tool:
    @staticmethod
    def yesorno(output_str):
        while True:
            s = input(tool.colorful(output_str + " [Y/n] ", "purple"))
            if s in "Yy":
                return True
            elif s in "Nn":
                return False

    @staticmethod
    def colorful(string, color):
        if platform.system().lower() == "linux":
            color_code = {
                "none": "\033[0m",
                "black": "\033[0;30m",
                "dark_gray": "\033[1;30m",
                "blue": "\033[0;34m",
                "light_blue": "\033[1;34m",
                "green": "\033[0;32m",
                "light_green": "\033[1;32m",
                "cyan": "\033[0;36m",
                "light_cyan": "\033[1;36m",
                "red": "\033[0;31m",
                "light_red": "\033[1;31m",
                "purple": "\033[0;35m",
                "light_purple": "\033[1;35m",
                "yellow": "\033[0;33m",
                "light_yellow": "\033[1;33m",
                "white": "\033[0;37m",
                "light_white": "\033[1;37m"
            }
            return color_code[color] + string + color_code["none"]
        else:
            return string

    @staticmethod
    def readable_byte(value):
        unit = ["B", "KB", "MB", "GB"]
        level = 0
        while (value >= 1024):
            value /= 1024
            level += 1
        return "%.2f %s" % (value, unit[level])

    @staticmethod
    def download_version(url, new_version, ignore_version):
        def download(url):
            requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
            ses = requests.session()
            ses.keep_alive = False  # 关闭多余连接
            try:
                return ses.get(url)
            except:
                print("fail to get from :\n", "   ", url)
                exit()

        print("Warning: It will change your default config in the script.")
        print("You can use \"-config_dump\" to dump your default json.")
        input(tool.colorful("-----press enter to continue-----", "red"))
        print("Current version :", version)
        print("Upgrade to :", new_version)
        if version == "latest":
            url += "/latest"
        else:
            url += "/tags/" + new_version
        print("Get", new_version, "version description from :\n" + "   ", url)
        version_json = download(url).json()
        # url 获取错误
        if "message" in version_json:
            print("Api message:", version_json["message"])
            print("Check the url or the version name")
            return
        # 需要更新至最新版 但已经是最新版
        if new_version == "latest" and version_json["tag_name"] == version:
            print("Already the latest version")
            print("Use \"-get %s\" to compulsory upgrade" % version)
            return
        # ignore version
        if new_version == "latest" and version_json[
                "tag_name"] in ignore_version:
            print("Latest version is %s. Ignored" % version_json["tag_name"])
            return
        print("Successfully get version json, download file")
        for asset in version_json["assets"]:
            file_name = asset["name"]
            if file_name == "data_maker.py":
                file_name = sys.argv[0].split('/')[-1]
            else:
                while os.path.isfile(file_name):
                    file_name = "new_" + file_name
            print("Download \"%s\" and save as \"%s\"" %
                  (asset["name"], file_name))
            res = download(asset["browser_download_url"])
            with open(file_name, "wb") as fl:
                fl.write(res.content)
        print("Successfully get the version:", version_json["tag_name"])
        print("Use \"-get %s\" to back to old version" % version)
        print("Version", version_json["tag_name"],
              "description:\n" + version_json["body"])


class file_oper:
    @staticmethod
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

    @staticmethod
    def file_head(file_name):
        with open(file_name, 'r') as fp:
            file_content = fp.readline()
            if len(file_content) > 50:
                return file_content[:50] + "..."
            if len(file_content) > 0 and file_content[-1] == '\n':
                return file_content[:-1]

    @staticmethod
    def check_empty(check_list):
        have_err = False
        for file_name in check_list:
            if os.path.getsize(file_name) == 0:
                print(tool.colorful(file_name + " is empty", "purple"))
                have_err = True
        if have_err:
            input(tool.colorful("-----存在空文件---按回车继续-----", "yellow"))

    @staticmethod
    def exec_thread_pool(thread_pool, multi_thread=False):
        def thread_pool_watcher():
            char = ['\\', '|', '/', '—']
            cnt = 0
            i = 0
            while cnt != len(thread_pool):
                time.sleep(0.1)
                cnt = 0
                i += 1
                for thread in thread_pool:
                    if thread.isAlive():
                        print("✗", end="")
                    else:
                        print("✓", end="")
                        cnt += 1
                print(" %2d/%2d  %c\r" % (cnt, len(thread_pool), char[i % 4]),
                      end="")
            print("✓" * len(thread_pool), "%2d/%2d" % (cnt, len(thread_pool)),
                  "done")

        watcher = threading.Thread(target=thread_pool_watcher)
        watcher.start()
        for thread in thread_pool:
            thread.start()
            if not multi_thread:
                thread.join()
        watcher.join()


class workflow(explainer):
    garbage = list()
    state = list()

    def __init__(self,
                 json_name="config.json",
                 args_str=None,
                 multi_thread=False):
        explainer.__init__(self, json_name, args_str)
        self.multi_thread = multi_thread

    def work(self):
        self.pre_compile()
        if "in" not in self.option.skip:
            self.make_temp_dir()
            self.get_state(self.json_data["state_name"])
            self.make_input_data()
        if "out" not in self.option.skip:
            self.make_output_data()
        if "zip" not in self.option.skip:
            self.zipped(self.zip_list, self.zip_name)
        self.clean()
        print(tool.colorful("-----完成-----", "red"))

    def make_temp_dir(self):
        if os.path.isdir("temp"):
            shutil.rmtree("temp")
        os.mkdir("temp")

    def get_state(self, state_name):
        try:
            with open(state_name, mode='r') as state_file:
                self.state = state_file.read().split('\n')
            while "" in self.state:
                self.state.remove("")
        except FileNotFoundError:
            print("\"%s\" not found" % self.json_data["state_name"])
            exit()

    def pre_compile(self):
        def cpp_compile(file_name):
            file_head = os.path.splitext(file_name)[0]
            print(f"编译 {file_head}.cpp")
            message = os.popen(self.json_data["compile_cmd"]["cpp"].format(
                file_head=file_head)).read()
            # if message.count("error") != 0:
            print("%5d error" % message.count("error"))
            # if message.count("warning") != 0:
            print("%5d warning" % message.count("warning"))
            if message.count("error") > 0:
                print(tool.colorful("-----编译错误-----", "red"))
                print(message)
                exit()
            self.garbage.append(file_head + ".out")

        if "in" not in self.option.skip and self.input_exec_type() == "cpp":
            cpp_compile(self.input_exec_name())
        if "out" not in self.option.skip and self.output_exec_type() == "cpp":
            cpp_compile(self.output_exec_name())

    def make_input_data(self):
        #构造数据
        if not os.path.isfile(self.input_exec_name()):
            print("\"%s\" not found" % self.input_exec_name())
            exit()
        print("数据生成中:")
        file_oper.exec_thread_pool(thread_pool=[
            threading.Thread(target=file_oper.popen,
                             args=(self.input_exec_cmd(), "str", self.state[i],
                                   "file",
                                   os.path.join("temp",
                                                self.input_name(i + 1))))
            for i in range(len(self.state))
        ],
                                   multi_thread=self.multi_thread)
        #编辑input
        if self.option.input_edit_num >= 0:
            for i in range(self.option.input_edit_num, 0, -1):
                os.system(f"code temp/{self.input_name(i)}")
            input("-----等待更改完成---按回车继续-----")
        file_oper.check_empty([
            os.path.join("temp", self.input_name(i + 1))
            for i in range(len(self.state))
        ])

    def make_output_data(self):
        if not os.path.isfile(self.output_exec_name()):
            print("\"%s\" not found" % self.output_exec_name())
            exit()
        print("结果生成中:")
        file_oper.exec_thread_pool(thread_pool=[
            threading.Thread(target=file_oper.popen,
                             args=(self.output_exec_cmd(), "file",
                                   os.path.join("temp",
                                                self.input_name(i + 1)),
                                   "file",
                                   os.path.join("temp",
                                                self.output_name(i + 1))))
            for i in range(len(self.state))
        ],
                                   multi_thread=self.multi_thread)
        #check empty
        file_oper.check_empty([
            os.path.join("temp", self.output_name(i + 1))
            for i in range(len(self.state))
        ])
        #print output
        if self.option.output_print:
            for i in range(1, len(self.state) + 1):
                print("%2d: %s" %
                      (i,
                       file_oper.file_head(
                           os.path.join("temp", self.output_name(i)))))
            input("-----显示结果完成---按回车继续-----")

    def zipped(self, zip_list, zip_name):
        for file_name in zip_list:
            shutil.copyfile(file_name, os.path.join("temp", file_name))
        if os.path.isfile(zip_name + ".zip"):
            if not tool.yesorno("是否覆盖已有Zip?(%s)" % zip_name):
                while os.path.isfile(zip_name + ".zip"):
                    zip_name = "new_" + zip_name
        print("打包数据中\r", end="")
        shutil.make_archive(base_name=zip_name, format="zip", root_dir="temp")
        zip_size = tool.readable_byte(os.path.getsize(zip_name + ".zip"))
        print(f"打包数据完成:  {zip_name}.zip  {zip_size}" + "\33[K")

    def clean(self, clean_temp_dir=True):
        if clean_temp_dir:
            shutil.rmtree("temp")
        for file_name in self.garbage:
            os.remove(file_name)


if __name__ == "__main__":
    try:
        work = workflow(json_name="config.json", multi_thread=True)
        work.work()
    except KeyboardInterrupt:
        try:
            work.clean(clean_temp_dir=False)
        except:
            pass
        print()