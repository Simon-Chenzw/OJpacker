import os
import platform


class execfile:
    """
    a class save the description of the execute file.  
    you can you macro {src} {exe} in "command" 
    """
    def __init__(self, src, exe=None, compile_cmd=None, execute_cmd=None):
        self.src = src
        self.exe = exe
        self.compile_cmd = compile_cmd
        self.execute_cmd = execute_cmd

    def compile(self):
        return self.compile_cmd.format(src=self.src, exe=self.exe)

    def execute(self):
        return self.execute_cmd.format(src=self.src, exe=self.exe)


class cppfile(execfile):
    """
    base on execfile,  
    compile cmd: "g++ {src} -o {exe} -std=c++17 -O3 -Wall",  
    the suffix of {exe} defaults to ".out" and ".exe" on Windows
    """
    def __init__(self, src):
        suffix = ".out"
        if platform.system().lower() == "windows":
            suffix = ".exe"
        execfile.__init__(self, src,
                          os.path.splitext(src)[0] + suffix,
                          "g++ {src} -o {exe} -std=c++17 -O3 -Wall", "./{exe}")


class py3file(execfile):
    """
    base on execfile, use python3
    """
    def __init__(self, src):
        execfile.__init__(self, src=src, execute_cmd="python3 {src}")


class statefile:
    """
    a class save everything about state
    """
    def __init__(self, name="state"):
        self.name = name

    def __len__(self):
        return len(self.data)

    def load(self):
        with open(self.name, "r") as state_file:
            self.data = state_file.readlines()

    def get(self, num):
        """
        return one line of the state  
        0 means the first one
        """
        return self.data[num]


class datafile:
    """
    a class save data description,  
    use macro {num} to replace the number in the name
    """
    def __init__(self, name, start_num=1):
        self.name = name
        self.start_num = start_num

    def get_name(self, num):
        """
        return the final name of the file  
        0 means the first one
        """
        return self.name.format(num=self.start_num + num)
