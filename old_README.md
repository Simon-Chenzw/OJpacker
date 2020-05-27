# 简介
一个简单的跨平台脚本，只需准备好所需程序，便可自动执行，自动打包。  
Script for packer test data for Olympic informatics Online Judge

## Instruction
See demo (version: v1.2.0) for details

## 使用方法
+ 下载`release`中的`python`脚本
+ 创建运行所需要的文件
+ `./data_maker.py` 运行脚本 *(linux下需要给予可执行权限)* 
+ `-h` 获取参数指南

## 运行所需要的文件
+ `states` 储存有传递给make_in的数据，每个数据点一行，空行将被忽略
+ `make_in.py` 读入states中的一行 输出一个题目的输入数据
+ `make_out.cpp` 读入一个题目的输入数据 输出一个题目的输出数据
+ tips
    + `make_in` 和 `make_out` 现支持 `C++` 和 `Python`
    + `C++`的源码将会自动编译，生成的可执行文件也会自动清理
    + `Python`解释器默认为`Python3`，若要使用`Python2`或`Pypy`，请自行更改config中的命令
    + 所有需求文件，都可在配置中更改名字

## 备注
+ 组织格式详见demo (version: v1.2.0)
+ 请勿短时间内频繁更新，避免被github拒绝访问。当拒绝时，稍等几分钟多试几次便可。
+ 推荐搭配`luogu`的Python数据生成器[CYaRon](https://github.com/luogu-dev/cyaron)使用

## 配置文件
+ 内置有默认配置文件
+ `-config_dump` 可以生成配置文件
+ 读取配置文件时是逐key覆盖默认配置
+ `-config_load` 可以将内置默认配置文件改为现在的配置文件
+ 参数详解:
    + ignore_version: 忽略的版本 当通过-upgrade升级时 会直接忽略
    + default_zip_name: 默认的zip文件名
    + default_input_exec_type: 默认构造输入数据的语言
    + default_output_exec_type: 默认构造输出数据的语言
    + states_name: states文件名
    + input_file_name: 输入数据 文件名模板
    + output_file_name: 输出数据 文件名模板
    + input_exec_name_list: 构造输入数据 各种语言的文件名
    + output_exec_name_list: 构造输出数据 各种语言的文件名
    + compile_cmd: 各种语言的编译命令
    + exec_cmd: 各种语言的运行命令
    + ~~zip_cmd: 压缩命令~~ **已经不需要了**
    + github_url: 获取脚本更新的api
+ 默认配置:
    ```json
    {
        "ignore_version": [],
        "default_zip_name": "problem_data",
        "default_input_exec_type": "py",
        "default_output_exec_type": "cpp",
        "states_name": "states",
        "input_file_name": "data%d.in",
        "output_file_name": "data%d.out",
        "input_exec_name_list": {
            "py": "make_in.py",
            "cpp": "make_in.cpp"
        },
        "output_exec_name_list": {
            "py": "make_out.py",
            "cpp": "make_out.cpp"
        },
        "compile_cmd": {
            "_comment": "file_head is the name you set in exec_name_list without suffix",
            "cpp": "g++ {file_head}.cpp -o {file_head}.out -std=c++17 -O3 2>&1"
        },
        "exec_cmd": {
            "_comment": "file_head is the name you set in exec_name_list without suffix",
            "py": "python3 {file_head}.py",
            "cpp": "./{file_head}.out"
        },
        "zip_cmd": "cd temp && zip -q -m -r ../{zip_name}.zip .",
        "github_url": "https://api.github.com/repos/Simon-Chenzw/data_maker/releases"
    }
    ```