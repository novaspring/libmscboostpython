# ----------------------------------------------------------------------------------
#  Title      : Bootstrap libMscBoostPython
#  Project    : libMscBoostPython
# ----------------------------------------------------------------------------------
#  File       : bootstrap_msc_boost_python.py
#  Author     : Stefan Reichoer
#  Company    : MSC Technologies
#  Created    : 2016-06-27
# ----------------------------------------------------------------------------------
#  Description: Download libMscBoostPython when necessary
# ----------------------------------------------------------------------------------
#  Copyright (c) 2016 -- MSC Technologies
# ----------------------------------------------------------------------------------

import os
import shutil
import sys

MSC_LDK_GIT_SERVER = "gitosis@msc-aac-debian01.msc-ge.mscnet:"

def check_for_pip3():
    pip3_available = shutil.which("pip3")
    if not pip3_available:
        return ["sudo apt-get install python-pip3"]
    return []

class PipInstall(object):
    def __init__(self, module_name, pip_package_name):
        self.module_name = module_name
        self.pip_package_name = pip_package_name
    def check(self):
        try:
            exec("import %s" % self.module_name)
        except ImportError:
            return ["sudo pip3 install %s" % self.pip_package_name]
        return []

class WorkingDirectory(object):
    def __init__(self, directory):
        self.directory = directory
        self.old_dir = os.getcwd()
        os.chdir(directory)
    def __enter__(self):
        return None
    def __exit__(self, type_, value_, traceback_):
        if type_:
            print("Error during processing in '%s'" % self.directory, file=sys.stderr)
        os.chdir(self.old_dir)
        return False

def run_cmd(cmd):
    print("Executing '%s'" % cmd)
    os.system(cmd)

def get_git_branch_name():
    return os.popen("git rev-parse --abbrev-ref HEAD").read().strip()

def get_git_tags():
    return os.popen("git tag").read().split()

def git_clone_msc_boost_python(branch, tag=None):
    if branch is not None:
        the_branch = "-b '%s'" % branch
    else:
        the_branch = ""
    cmd = "git clone %s/msc/0000/libMscBoostPython" % MSC_LDK_GIT_SERVER
    run_cmd(cmd)
    checkout_cmd = "git checkout -b %s" % branch
    if tag is not None:
        checkout_cmd += " %s" % tag
    with WorkingDirectory("libMscBoostPython"):
        run_cmd(checkout_cmd)

def check_python_requirements():
    command_list = []
    command_list.extend(check_for_pip3())

    git_python = PipInstall("git", "gitpython")
    command_list.extend(git_python.check())
    if command_list:
        print("Dependencies for libMscBoostPython are not met")
        print("Please issue the following commands:")
        print("\n".join(command_list))
        return False
    return True

def install_msc_boost_python():
    branch_name = get_git_branch_name()
    tags = get_git_tags()
    print("install_msc_boost_python: branch: %s, tags: %s" % (branch_name, tags))
    if not os.path.isdir("libMscBoostPython"):
        git_clone_msc_boost_python(branch_name)
        os.symlink("libMscBoostPython/src/MscBoost", "MscBoost")

def bootstrap_msc_boost_python():
    if check_python_requirements():
        install_msc_boost_python()
        return
    sys.exit(1)
