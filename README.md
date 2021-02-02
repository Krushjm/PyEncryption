# PyEncryption

[English Readme](https://github.com/Krushjm/PyEncryption/blob/master/README_en.md)

PyEncryption 是一个基于 [py2sec](https://github.com/cckuailong/py2sec) / [py2so](https://github.com/cckuailong/py2so) 项目的 Python 文件加密脚本

### New

* 增加命令行参数 `-m / --mode`，当 `mode='classical' 时，将原项目所有文件拷贝到目标路径中，具体参数请参考文档

### Change

* 原命令行参数 `-m / --maintain` 修改为 `-e / --exclude`

### Fix

* 在 Windows 系统下文件路径 `.\` 导致无法编译的问题

以下为文档（有更新内容）

py2sec 一款轻量的脚本工具，基于 Cython 将 .py 编译成 run-time libraries 文件：.so (Linux && Mac)，或 .pyd (Win)。一定程度上实现了“加密”保护源代码的需求。

## 系统支持

Linux && MacOS && Windows

注意：Windows用户运行时可能会遇到如下错误

```
error: command 'cl.exe' failed: No such file or directory
```

请安装对应Win系统版本的Visual C++ Build Tools

## py2sec 特性

1. .so / .pyd 文件可以像 .py 模块一样正常调用。例如：`import` 或 `from module import * "`
2. py2sec 可以指定编译单个 .py 文件，也可以指定一个 python 项目目录
3. py2sec 还可以提升代码运行速度，至多提升30倍
4. py2sec 自动识别项目中的 .py 文件，且只编译 .py 类型文件
5. 可以指定不需要编译的文件或子目录
6. py2sec 不影响源文件，加密后的文件或项目将被存放在 result 文件夹
7. 兼容多平台：macOS、Linux、Windows、
8. 兼容 Python 版本：python2 and python3, 可使用 -p(--py) 参数来指定版本
9. 支持多线程（待改进）

## 环境配置

```
pip install requirements.txt
```

## 使用说明

### 使用

```
python py2sec.py [选项] ...
```

### 选项

```
-v,  --version    显示 py2sec 版本
-h,  --help       显示帮助菜单
-p,  --pyth       Python的版本, 默认为 你的 "python" 命令绑定的python版本
                  例: -p 3  (比如你使用 python3)
-d,  --directory  Python 项目路径 (如果使用 -d 参数, 将编译整个 Python 项目)
-f,  --file       Python 文件 (如果使用 -f, 将编译单个 Python 文件)
-m   --mode       运行模式，仅在使用 -d 时有效，值为 'minimal'，'classic' 或 'inplace'
                        minimal: 编译 .py 文件并存放到 result 文件夹下
                        classic: 编译 .py 文件并将其他项目文件一起存放到 result 文件夹下
                        inplace: 编译 .py 文件存放到源文件夹下，并删除源文件（未实现）
-e,  --exclude    标记你不想编译的文件或文件夹路径
                  注意: 文件夹需要以路径分隔符号（`/`或`\\`，依据系统而定）结尾，并且需要和-d参数一起使用 
                  例: -m setup.py,mod/__init__.py,exclude_dir/
-x  --nthread     编译启用的线程数
-q  --quiet       静默模式，默认 False
-r  --release     Release 模式，清除所有中间文件，只保留加密结果文件，默认False
```

```
python py2sec.py -f test.py
python py2sec.py -f example/test1.py -r
python py2sec.py -d example/ -m test1.py,bbb/

# 一些操作系统使用 "python3" 命令来执行python3，如Ubuntu，这里可以使用 -p 参数来运行
python3 py2sec.py -p 3 -d example/
```

### 项目结构

- build/                    临时文件夹, .o, .so/.pyd 文件
- tmp_build/                临时文件夹, .c 文件
- result/                   编译最终结果存放目录
- result/log.txt            编译过程日志
- py2sec.py                 主函数文件
- py2sec_build.py.template  用于生成 py2sec_build.py 的模板文件
- requirements.txt          依赖库的清单

### 注意事项
1. 请将要加密的目录或文件存放在与 `py2sec.py` 同级目录下
2. 编译后的项目启动文件请使用以项目为根目录的导入语句，如 `from example.aaa import test1`
3. Windows 平台需要安装 [C++ 编译工具](https://visualstudio.microsoft.com/zh-hans/visual-cpp-build-tools/)

### 协议

本项目遵循MIT协议

### 示例

整个Python项目编译前:

![demo1](img/1.png)

py2sec 编译后效果:

![demo2](img/2.png)
