# 简介
一个简单的 python 脚本工具，简化生成数据的过程。  
a script can packer test data for Olympic informatics Online Judge

## 简单使用指南
+ 安装: `pip3 install ojpacker`
+ 更新: `pip3 install --upgrade ojpacker`
+ 运行:
    1. 直接在终端中输入 `ojpacker` ，即可在当前目录运行
        * 需要 pip 自动添加的脚本的所在目录在 `PATH` 中，若提示 `ojpacker` 不存在，请检查 `PATH`
    2. 运行 `python3 -m ojpacker`
+ 演示: 运行 `ojpacker demo` 可以生成demo文件夹，内含几个文件，在预配置的编译命令正确的情况下可以直接运行

## 环境要求 (probably)
+ python >= 3.6.9
+ [rich](https://github.com/willmcgugan/rich) >= 3.0

# 文档
## 目录：
1. [工作原理](#工作原理)
2. [命令行参数](#命令行参数)
3. [配置文件及其内容](#配置文件及其内容)

## 工作原理
举个例子，demo里除去配置有三个文件：
+ state
+ make_in
+ make_out  
    注意：以上所有的文件名都可在配置中修改

### 典型流程
一个典型的题目构造流程，主要分为两部分。分别是构造in文件和out文件  
* #### 构造in文件
    本程序将会从 state 中逐行读入，再将读入的数据传递给 make_in  
    而 make_in 则依据读入的数据生成一个in文件
* #### 构造out文件
    本程序将依照配置中对数据点命名的格式，在文件夹中依次查找in文件  
    当文件存在时，将交由 make_out 文件构造一个同样序号的out文件

在这两个流程结束后，将会对生成的数据进行压缩打包，此阶段可以使用命令行参数 `-unzip` 跳过

### 特殊流程
不是所有的构造都需要同时运行两个流程，所以在命令行参数中使用 `-input` 与 `-output` 可以跳过相关的流程，详见命令行参数的对应条目

### 文件要求：
1. state:
    * 每行依次代表了构造in数据点时的所需参数
    * 空行代表没有这个数据点，对应的序号也将跳过
2. make_in 与 make_out:
    * 只需准备源文件， 如有需要会自动编译，但需配置编译命令
    * 输入输出均使用标准输入输出
3. 配置文件
4. 缓存目录：
    * 运行时需要缓存目录 temp，此目录开始时会自动创建，结束时会自动销毁。
    * **若开始运行时目录已存在，将会直接删除！！！**

## 命令行参数
提示：在参数不会产生歧义的情况下，可以只打第一个或者前几个字母。
### 所有命令
1. [主命令](#主命令)
2. [config](#config命令)
3. [demo](#demo命令)

### 主命令
控制运行流程的相关参数
* `-log LEVEL` :
    此命令将会指定运行时输出日志的等级，默认等级为 info，可选等级有：
    * error
    * warning
    * info
    * debug

* `-name FILENAME` :
    指定压缩包、文件夹的名字，不包含后缀名，不指定时使用配置中的默认值 `defalut_zip_name`

* `-show` :
    生成完成 in/out 文件时，打印文件的第一行
    * 选项后可接一个 `input` 或 `output` ，代表仅打印指定的一种

* `-dir directory` :
    当你跳过生成 in文件的阶段时，可以指定一个文件夹，使 make_out 从中读取数据。若未指定，则从 temp 目录读取

* `-input NAME` :
    指定 make_in 文件
    * 这里的NAME不是文件名，而是配置中的代号，详见配置文件的 `input_exec`
    * 若没有这个参数，将会使用配置中的 `input_default_exec`
    * 若 NAME 在配置中不存在，则会跳过此阶段

* `-output NAME` :
    指定 make_out 文件
    * 这里的NAME不是文件名，而是配置中的代号，详见配置文件的 `output_exec`
    * 若没有这个参数，将会使用配置中的 `output_default_exec`
    * 若 NAME 在配置中不存在，则会跳过此阶段

* `-unzip` :
    跳过最后压缩文件夹的过程，将数据保存在一个文件夹中

* `-addzip FILE...` :
    后接参数为文件名，这些文件将会在构造完数据之后一起压缩，或移动至文件夹中

* `-multiprocess [Max]` :
    使用多进程运行 make_in 与 make_out ，Max 为最大进程数，不指定为无上限

### config命令
config 是配置文件相关的命令，单独运行无效果

* `-create` :
    在当前目录中，使用 demo 的配置，创建一个配置文件

* `-copyto user/local` :
    将配置文件从 local 拷贝至 user，或从 user 拷贝至 local 。详见配置文件

### demo命令
直接运行demo，会产生一个文件夹，内含有产生A+B题目的演示

* `-dir [directory]` :
    指定文件名，若 directory 留空则在当前目录创建

## 配置文件及其内容
* 配置文件名为 ojpacker.json
* 配置文件分为两种，当前目录的称为local，`~/.config/` 下的称为user。当local存在时使用local，否则使用user

### json各参数详解
json内容为字典，以下是各个键值的意义

* 字符串：
    * `defalut_zip_name` :
        未使用 `-name` 参数时，所采用的压缩包名、文件夹名

    * `state_name` :
        state 文件的名字

    * `input_data_name` :
        in数据的文件名，使用 `{num}` 代替数字，从1开始编号

    * `output_data_name` :
        out数据的文件名，使用 `{num}` 代替数字，从1开始编号

    * `input_default_exec` :
        默认使用的 make_in 文件代号

    * `output_default_exec` :
        默认使用的 make_out 文件代号
* [execfile](#execfile)：
    * `input_exec` :
        make_in 文件配置，详见下面的[`execfile`](#execfile)

    * `output_exec` :
        make_out 文件配置，详见下面的[`execfile`](#execfile)

### execfile
execfile 的格式为 json 的字典，以 demo 中 C++ 的 make_in 配置为例
```json
"cpp": {
    "src": "make_out.cpp",
    "exe": "make_out.out",
    "compile_cmd": "g++ {src} -o {exe}",
    "execute_cmd": "./{exe}"
}
```
1. `cpp` 是其代号，此代号在命令行参数 `-input` 和 `-output` 以及配置中 `input_default_exec` 与 `output_default_exec` 中使用
2. `src` 源代码文件名
3. `exe` 可执行文件文件名
4. `compile_cmd` 编译命令
5. `execute_cmd` 执行命令  
    注意：
    1. 若所使用的语言没有编译阶段， `exe` 与 `compile_cmd` 可留空
    2. 命令中可以使用 `{src}` 与 `{exe}` 代替相应的文件名