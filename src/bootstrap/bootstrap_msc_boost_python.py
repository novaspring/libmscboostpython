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

try:
    MAIN_SCRIPT_DIR = os.path.dirname(os.path.realpath(sys.modules['__main__'].__file__))
except AttributeError:
    MAIN_SCRIPT_DIR = os.getcwd()

MSC_GIT_SERVER = os.environ.get("MSC_GIT_SERVER_CACHE", "ssh://gitolite@msc-git02.msc-ge.com:9418/")

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
    return True

def get_git_branch_name():
    return os.popen("git rev-parse --abbrev-ref HEAD").read().strip()

def get_git_tags():
    return os.popen("git tag").read().split()

def get_git_branches():
    branches = os.popen("git branch").read().split("\n")
    branches.sort(reverse=True)
    branches = [branch.lstrip(" *") for branch in branches if branch]
    return branches

def git_clone_msc_boost_python(branch, tag=None):
    cmd = "git clone %s/msc/0000/libMscBoostPython" % MSC_GIT_SERVER
    if run_cmd(cmd):
        with WorkingDirectory("libMscBoostPython"):
            msc_boost_python_branches = get_git_branches()
            if branch in msc_boost_python_branches:
                pass
            elif branch.startswith("feature"):
                branch = "develop"
            else:
                branch = "master"
            checkout_cmd = "git checkout -b %s" % branch
            if tag is not None:
                checkout_cmd += " %s" % tag
            run_cmd(checkout_cmd)
            upstream_set_cmd = "git branch --set-upstream-to=origin/%s %s" % (branch, branch)
            run_cmd(upstream_set_cmd)
            run_cmd("git pull")
            return True
    return False

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
    with WorkingDirectory(MAIN_SCRIPT_DIR):
        branch_name = get_git_branch_name()
        if not os.path.isdir("libMscBoostPython"):
            git_clone_msc_boost_python(branch_name)
            if not os.path.islink("MscBoost"):
                os.symlink("libMscBoostPython/src/MscBoost", "MscBoost")

def bootstrap_msc_boost_python():
    if check_python_requirements():
        install_msc_boost_python()
        return
    sys.exit(1)
