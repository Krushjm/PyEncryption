"""

Project:       py2sec
File:          py2sec.py
Edit_time:     2021/1/30 11:40
--------------------------------------------
Author:        Krus Han
Contact:       https://github.com/Krushjm

"""

import getopt
import os
import sys
import subprocess
import shutil
import platform
from typing import Optional, List, Union


class BuildOptions:

    def __init__(self):
        self.python_version = ''
        self.file_name = ''
        self.root_name = ''
        self.exclude = []
        self.n_jobs = '1'
        self.quiet = "False"
        self.release = False


is_windows = True if platform.system() == 'Windows' else False

py2sec_version = ('0', '3', '1')

HELP_TEXT = """
py2sec is a Cross-Platform, Fast and Flexible tool to compile the .py to .so(Linux and Mac) or .pdy(Win).
You can use it to hide the source code of py
It can be called by the main func as "from module import * "
py2sec can be used in the environment of python2 or python3

Usage: python py2sec.py [options] ...

Options:
  -v,  --version    Show the version of the py2sec
  -h,  --help       Show the help info
  -p,  --python     Python version, default is based on the version of python you bind with command "python" 
                    Example: -p 3  (means you tends to encrypt python3)
  -d,  --directory  Directory of your project (if use -d, you encrypt the whole directory)
  -f,  --file       File to be transferred (if use -f, you only encrypt one file)
  -e,  --exclude   List the file or the directory you don't want to transfer
                    Note: The directories should be suffix by path separate char ('\\' in Windows or '/'), 
                    and must be the relative path to -d's value
                    Example: -m setup.py,mod/__init__.py,exclude_dir/
  -x,  --n_jobs     number of parallel thread to build jobs
  -q   --quiet      Quiet Mode, Default: False
  -r   --release    Release Mode, clear all the tmp files, only output the result, Default: False


Example:
  python py2sec.py -f test.py
  python py2sec.py -f example/test1.py -r
  python py2sec.py -d example/ -m test1.py,bbb/

  # some OS use command "python3" to run python3, like Ubuntu, you can use -p to solve it
  python3 py2sec.py -p 3 -d example/
"""

build_script_name = 'tmp_py2sec_build.py'
build_script_temp_name = 'py2sec_build.py.template'


def get_file_name(
        dir_path,
        include_sub_dir=True,
        path_type=0,
        ext_names: Optional[Union[List[str], str]] = None
):
    """获得指定目录下的所有文件，
        :param dir_path: 指定的目录路径
        :param include_sub_dir: 是否包含子文件夹里的文件，默认 True
        :param path_type: 返回的文件路径形式
            0 绝对路径，默认值
            1 相对路径
            2 文件名
        :param ext_names: "*" | string | list
            可以指定文件扩展名类型，支持以列表形式指定多个扩展名。默认为 "*"，即所有扩展名。
            举例：".txt" 或 [".jpg",".png"]

        :return: 以 yield 方式返回结果

    Updated:
        2020-04-21
    Author:
        nodewee (https://nodewee.github.io)
    """

    # ext_names
    if type(ext_names) is str:
        if ext_names != "*":
            ext_names = [ext_names]
    # lower ext name letters
    if type(ext_names) is list:
        for i in range(len(ext_names)):
            ext_names[i] = ext_names[i].lower()

    def keep_file(name):
        if type(ext_names) is list:
            if name[0] == '.':
                file_ext = name
            else:
                file_ext = os.path.splitext(name)[1]
            #
            if file_ext.lower() not in ext_names:
                return False
        else:
            return True
        return True

    if include_sub_dir:
        path_len = len(dir_path)
        for root, dirs, files in os.walk(dir_path):
            for file_name in files:
                if not keep_file(file_name):
                    continue
                if path_type == 0:  # absolute path
                    yield os.path.join(root, file_name)
                elif path_type == 1:  # relative path
                    yield os.path.join(
                        root[path_len:].lstrip(os.path.sep), file_name)
                else:  # file name
                    yield file_name
    else:
        for file_name in os.listdir(dir_path):
            filepath = os.path.join(dir_path, file_name)
            if os.path.isfile(filepath):
                #
                if not keep_file(file_name):
                    continue
                #
                if path_type == 0:
                    yield filepath
                else:
                    yield file_name


def make_dirs(dir_path):
    """
    创建目录
        支持多级目录，若目录已存在自动忽略
        Updated: 2020-02-27
        Author: nodewee (https://nodewee.github.io)
    """

    dir_path = dir_path.strip().rstrip(os.path.sep)

    if dir_path:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)


def get_command_options(build_options):
    try:
        print(sys.argv[1:])
        options, _ = getopt.getopt(sys.argv[1:], "vhp:d:f:e:x:qr", [
            "version", "help", "python=", "directory=", "file=", "exclude=",
            "n_jobs=", "quiet", "release"
        ])
    except getopt.GetoptError:
        print("Get options Error")
        print(HELP_TEXT)
        sys.exit(1)

    for key, value in options:
        if key in ["-h", "--help"]:
            print(HELP_TEXT)
            sys.exit(0)
        elif key in ["-v", "--version"]:
            print("py2sec version {0}".format('.'.join(py2sec_version)))
            sys.exit(0)
        elif key in ["-p", "--python"]:
            build_options.python_version = value
        elif key in ["-d", "--directory"]:
            if build_options.file_name:
                print("Canceled. Do not use -d -f at the same time")
                sys.exit(1)
            if value[-1] == '/':
                build_options.root_name = value[:-1]
            else:
                build_options.root_name = value
            while build_options.root_name.startswith('.') or build_options.root_name.startswith('\\'):
                build_options.root_name = build_options.root_name[1:]
        elif key in ["-f", "--file"]:
            if build_options.root_name:
                print("Canceled. Do not use -d -f at the same time")
                sys.exit(1)
            build_options.file_name = value
            while build_options.file_name.startswith('.') or build_options.file_name.startswith('\\'):
                build_options.file_name = build_options.file_name[1:]
        elif key in ["-e", "--exclude"]:
            for path_assign in value.split(","):
                if not path_assign[-1:] in ['/', '\\']:  # if last char is not a path sep, consider it's assign a file
                    build_options.exclude.append(path_assign)
                else:  # assign a dir
                    assign_dir = path_assign.strip('/').strip('\\')
                    tmp_dir = os.path.join(options.root_name, assign_dir)
                    files = get_file_name(dir_path=tmp_dir,
                                          include_sub_dir=True,
                                          path_type=1)
                    #
                    for f in files:
                        file_path = os.path.join(assign_dir, f)
                        build_options.exclude.append(file_path)

        elif key in ["-x", "--n_jobs"]:
            build_options.n_jobs = value
        elif key in ["-q", "--quiet"]:
            build_options.quiet = "True"
        elif key in ["-r", "--release"]:
            build_options.release = True

    return build_options


def get_encrypt_file_list(options):
    file2compiler = []

    #
    if options.root_name != '':
        if not os.path.exists(options.root_name):
            print("No such Directory, please check or use the Absolute Path")
            sys.exit(1)

        #
        pyfiles = get_file_name(dir_path=options.root_name,
                                include_sub_dir=True,
                                path_type=1,
                                ext_names='.py')

        # filter exclude files
        tmp_files = list(set(pyfiles) - set(options.exclude))
        file2compiler = []
        for f in tmp_files:
            file2compiler.append(os.path.join(options.root_name, f))

    #
    if options.file_name != '':
        if options.file_name.endswith(".py"):
            file2compiler.append(options.file_name)
        else:
            print("Make sure you give the right name of py file")

    return file2compiler


def gen_setup(options, file2compiler):
    if os.path.exists(build_script_name):
        os.remove(build_script_name)
    with open(build_script_temp_name, "r") as f:
        template = f.read()
    files = '", r"'.join(file2compiler)
    cont = template % (files, options.python_version, options.n_jobs, options.quiet)
    with open(build_script_name, "w") as f:
        f.write(cont)


def clean_build_dirs():
    if os.path.isdir("build"):
        shutil.rmtree("build")
    if os.path.isdir("tmp_build"):
        shutil.rmtree("tmp_build")
    if os.path.isdir("result"):
        shutil.rmtree("result")


def clean_temp_files():
    if os.path.isdir("build"):
        shutil.rmtree("build")
    if os.path.isdir("tmp_build"):
        shutil.rmtree("tmp_build")
    if os.path.isfile("tmp_py2sec_build.py"):
        os.remove("tmp_py2sec_build.py")


def encrypt(options):
    # prepare folders
    make_dirs('build')
    make_dirs('tmp_build')

    if options.quiet == "True":
        log = "> log.txt"
    else:
        log = ""
    cmd = " {0} build_ext {1}".format(build_script_name, log)
    if options.python_version == '':
        cmd = 'python' + cmd
    else:
        cmd = 'python' + options.python_version + cmd
    if not is_windows:
        print('> pyEncrypt')
        print(cmd)
    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.STDOUT)
    code = p.wait()
    if code:
        print("\nPy2Sec Encrypt Encounter Error")
        sys.exit(1)


def gen_project(options):
    make_dirs('result')
    for file_name in get_file_name('build', True, 1, ['.so', '.pyd']):
        src_path = os.path.join('build', file_name)
        mid_path = os.path.sep.join(file_name.split(os.path.sep)[1:-1])
        file_name_parts = os.path.basename(src_path).split('.')
        file_name = '.'.join([file_name_parts[0]] + file_name_parts[-1:])
        path = os.path.join('result', mid_path, file_name)
        make_dirs(os.path.dirname(path))
        shutil.copy(src_path, path)
    if options.release:
        clean_temp_files()
    print("\nPy2Sec Encrypt Finished")


if __name__ == "__main__":
    opts = get_command_options(BuildOptions())
    will_compile_files = get_encrypt_file_list(opts)
    clean_build_dirs()
    if not is_windows:
        gen_setup(opts, will_compile_files)
        encrypt(opts)
    else:  # Windows OS
        for file in will_compile_files:
            gen_setup(opts, [file])
            encrypt(opts)

    gen_project(opts)
