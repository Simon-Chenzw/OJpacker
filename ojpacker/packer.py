from __future__ import absolute_import
import os
import shutil
import threading
from . import tool
from . import filetype
from . import fileutil


class packer:
    garbage = list()

    def __init__(self, zip_name="problem_data"):
        self.name = zip_name
        self.load_setting()
        self.load_file()

    def load_file(self,
                  state=None,
                  input_file=None,
                  output_file=None,
                  input_exec=None,
                  output_exec=None):
        self.state = state
        self.input_file = input_file
        self.output_file = output_file
        self.input_exec = input_exec
        self.output_exec = output_exec

    def load_setting(self,
                     edit=None,
                     showinput=False,
                     showoutput=False,
                     zip_list=[],
                     executive_part=["in", "out", "zip"],
                     multi_thread=False):
        self.edit = edit
        self.showinput = showinput
        self.showoutput = showoutput
        self.zip_list = zip_list
        self.executive_part = executive_part
        self.multi_thread = multi_thread

    def work(self):
        self.pre_compile(self.garbage)
        if "in" in self.executive_part:
            self.state.load()
            self.make_temp_dir()
            self.make_input_data()
        if "out" in self.executive_part:
            self.make_output_data()
        if "zip" in self.executive_part:
            self.zipped(self.zip_list, self.name)
            self.clean()
        else:
            self.clean(clean_temp_dir=False)
        print(tool.color("red", "-----完成-----"))

    def pre_compile(self, garbage):
        if "in" in self.executive_part:
            if self.input_exec is None:
                print(tool.color("red", "execute file of input not found"))
                exit()
            else:
                fileutil.compile(self.input_exec, garbage)
        if "out" in self.executive_part:
            if self.output_exec is None:
                print(tool.color("red", "execute file of output not found"))
                exit()
            else:
                fileutil.compile(self.output_exec, garbage)

    def make_temp_dir(self):
        if os.path.isdir("temp"):
            shutil.rmtree("temp")
        os.mkdir("temp")

    def make_input_data(self):
        #构造数据
        print("数据生成中:")
        thread_pool = [
            threading.Thread(target=fileutil.popen,
                             args=(self.input_exec.execute(), "str",
                                   self.state.get(i), "file",
                                   os.path.join("temp",
                                                self.input_file.get_name(i))))
            for i in range(len(self.state))
        ]
        tool.exec_thread_pool(thread_pool, self.multi_thread)
        #编辑input
        if self.edit is not None:
            for i in range(self.edit, 0, -1):
                os.system(f"code temp/{self.input_file.get_name(i)}")
            input("-----等待更改完成---按回车继续-----")
        fileutil.check_empty([
            os.path.join("temp", self.input_file.get_name(i))
            for i in range(len(self.state))
        ])

    def make_output_data(self):
        print("结果生成中:")
        i = 0
        thread_pool = []
        while os.path.isfile(os.path.join("temp",
                                          self.input_file.get_name(i))):
            thread_pool.append(
                threading.Thread(
                    target=fileutil.popen,
                    args=(self.output_exec.execute(), "file",
                          os.path.join("temp",
                                       self.input_file.get_name(i)), "file",
                          os.path.join("temp", self.output_file.get_name(i)))))
            i += 1
        tool.exec_thread_pool(thread_pool, self.multi_thread)
        #check empty
        fileutil.check_empty([
            os.path.join("temp", self.output_file.get_name(i))
            for i in range(len(thread_pool))
        ])
        #print output
        if self.showoutput:
            for i in range(len(thread_pool)):
                print(
                    "%2d: %s" %
                    (i + 1,
                     fileutil.file_head(
                         os.path.join("temp", self.output_file.get_name(i)))))
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