# 简介
一个简单的脚本，帮助你在出数据的时候，自动执行，自动打包。

## 使用方法
+ 下载`release`中的`python`脚本
+ `chmod +x data_maker.py` 给予可执行权限
+ 创建 
    - `states`
    - `make_in.py`
    - `make_out.cpp`
+ `./data_maker.py` 运行脚本，自动生成默认config.json

## 运行所需要的文件
+ `data_maker.py` 脚本本体
+ `config.json` 储存设置的json
+ `states` 储存给make_in的数据，每个数据点一行，空行将被忽略
+ `make_in.py` 读入states中的一行 输出一个题目的输入数据
+ `make_out.cpp` 读入一个题目的输入数据 输出一个题目的输出数据

## tips
+ `./data_maker.py -h` 获取参数指南
+ `make_in` 和 `make_out` 支持`C++` 和 `Python3`
+ C++的源码将会自动编译，生成的可执行文件也会自动清理
+ 运行所需要的文件，除 json 外，都可在 `config.json` 中更改名字
+ `config.json` 的名字也可更改，但需要修改脚本中 `config_json` 的值
+ 请勿短时间内频繁更新，避免被github拒绝访问。当拒绝时，稍等几分钟便可。

## json详解
```javascript
{
    "version": "v1.0.0",                // 标记当前版本 无需更改
    "ignore_version": [],               // 忽略的版本 当通过-upgrade升级时 会直接忽略
    "default_zip_name": "problem_data", // 默认的zip文件名
    "default_input_exec_type": "py",    // 默认的 构造输入数据的语言
    "default_output_exec_type": "cpp",  // 默认的 构造输出数据的语言
    "script_name": "work.py",           // 脚本文件名 更新下来的新版本会自动重命名至这个值
    "states_name": "states",            // states文件名
    "input_file_name": "data%d.in",     // 输入数据 文件名模板
    "output_file_name": "data%d.out",   // 输出数据 文件名模板
    "input_exec_name_list": {           // 构造输入数据 各种语言的文件名
        "py": "make_in.py",
        "cpp": "make_in.cpp"
    },
    "output_exec_name_list": {          // 构造输出数据 各种语言的文件名
        "py": "make_out.py",
        "cpp": "make_out.cpp"
    },
    "compile_cmd": {                    // 各种语言的编译命令
        "_comment": "file_head is the name you set in exec_name_list without suffix",
        "cpp": "g++ {file_head}.cpp -o {file_head}.out -std=c++17 -O3 2>&1"
    },
    // 压缩命令
    "zip_cmd": "cd temp && zip -q -m -r ../{zip_name}.zip .",   
    // 获取更新的api
    "github_url": "https://api.github.com/repos/Simon-Chenzw/data_maker/releases"
}
```