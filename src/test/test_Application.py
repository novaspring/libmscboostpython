import io
import MscBoost
import os
import pytest
import sys

import MscBoost.MscProject

from MscBoost.Application import _CompliantArgumentParser
from MscBoost.EnvironmentVariable import EnvironmentVariable
from MscBoost.Logging import Log
from MscBoost.UsageException import UsageException
from MscBoost.MscProject import MscProject

from io import StringIO

the_main_exception_message = "as requested"
the_verbose_0_msg = "verbose0"
the_verbose_1_msg = "verbose1"

class MyApplication(MscBoost.Application):
    def __init__(self,
                 name = "App",
                 short_help = "Help.",
                 main_will_fail = False,
                 use_test_helper_file_directory = True,
    ):
        super(self.__class__, self).__init__(name, short_help)
        self.in_main = False
        self.in_exit = False
        self.exit_code = 0
        self.main_will_fail = main_will_fail
        self.use_test_helper_file_directory = use_test_helper_file_directory

    def _main(self):
        self.in_main = True
        if self.main_will_fail:
            raise Exception(the_main_exception_message)
        Log().out(0, the_verbose_0_msg)
        Log().out(1, the_verbose_1_msg)

    def _exit(self, exit_code):
        self.in_exit = True
        self.exit_code = exit_code

    def _get_application_helper_file_search_directories(self):
        if self.use_test_helper_file_directory:
            search_dirs = [ os.path.join(MscProject.find_project_root(os.getcwd()), "src", "test") ]
        else:
            search_dirs = super(self.__class__, self)._get_application_helper_file_search_directories()
            if "." in search_dirs:
                search_dirs.remove(".")

        return search_dirs

def test_UsageException():
    msg = "What"
    e = UsageException(msg)
    assert str(e) == msg
    assert isinstance(e, Exception)

def test_CompliantArgumentParser():
    parser = _CompliantArgumentParser(
        prog = "dummy",
        add_help = False,
    )

    # Test compliant arguments
    with pytest.raises(AssertionError):
        parser.add_argument("-v", help="") # no help is an error
    with pytest.raises(AssertionError):
        parser.add_argument("-v", help="help must start capitalized.")
    with pytest.raises(AssertionError):
        parser.add_argument("-v", help="Help must end with '.'")

    # ********** Ensure that arguments are parsed
    store_cmdline_arg = "--store"
    parser.add_argument(store_cmdline_arg, action="store_true", help="Help.")
    # test empty list not failing
    parser.parse_args("".split())
    args = parser.parse_args(store_cmdline_arg.split())
    assert args.store == True

    store_cmdline_arg_t = store_cmdline_arg + "t"
    try:
        parser.parse_args(store_cmdline_arg_t.split())
    except MscBoost.UsageException as e:
        msg = str(e)
        expected = "Unknown command line option " + store_cmdline_arg_t + " - did you mean '" + store_cmdline_arg + "'?"
        assert expected == msg

def test_Application():
    # Compliance checks
    with pytest.raises(AssertionError):
        x = MyApplication("", "Help.") # no name is an error

    with pytest.raises(AssertionError):
        MyApplication("name", "") # no help is an error

    with pytest.raises(AssertionError):
        MyApplication("name", "help must start capitalized.")

    with pytest.raises(AssertionError):
        MyApplication("name", "Help must end with '.'")

    # ********** Ensure that main is called
    x = MyApplication("dummy", "Help.")
    # we need to replace the argv as py.test adds arguments which Application would wrongly interpret
    oldarg = sys.argv
    sys.argv = "test_Application.py".split()
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        assert not x.in_main
        x.run()
        assert x.in_main
        assert x.exit_code == 0
    finally:
        sys.argv = oldarg
        sys.stdout = old_stdout

    # ********** Ensure that there is a help with exit code 2
    # redirect output to string so we can analyze it
    x = MyApplication("dummy", "Help.")

    # register an environment variable
    env_dummy_name = "DUMMY"
    env_dummy_help = "Dummy application."
    env_dummy = EnvironmentVariable(env_dummy_name, env_dummy_help)

    assert not x.in_exit
    assert x.exit_code == 0
    oldarg = sys.argv
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    sys.argv = "test_Application.py --help".split()
    try:
        x.run()
    finally:
        output = sys.stdout.getvalue()
        sys.argv = oldarg
        sys.stdout = old_stdout
        assert "usage: dummy" in output
        assert x.in_exit
        assert x.exit_code == 2

        # Ensure that environment variables are listed:
        assert env_dummy_name in output
        assert env_dummy_help in output
        del(env_dummy)

    # ********** Ensure that suggestions are made on failure.
    # redirect output to string so we can analyze it
    x = MyApplication("dummy", "Help.")
    oldarg = sys.argv
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    existing_arg = "--help"
    non_existing_arg = existing_arg + "x"
    sys.argv = ("test_Application.py " + non_existing_arg).split()
    try:
        assert x.exit_code == 0
        x.run()
    finally:
        output = sys.stderr.getvalue()
        sys.argv = oldarg
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        expected = "Unknown command line option {0} - did you mean '{1}'?".format(
            non_existing_arg,
            existing_arg
            )
        assert expected in output
        assert x.exit_code == 1

    # ********** Ensure that error exceptions are handled.
    # redirect output to string so we can analyze it
    x = MyApplication("dummy", "Help.", main_will_fail = True)
    oldarg = sys.argv
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    sys.argv = ("test_Application.py").split()
    try:
        assert x.exit_code == 0
        x.run()
    finally:
        output = sys.stderr.getvalue()
        sys.argv = oldarg
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        expected = "*** ERROR: " + the_main_exception_message
        assert expected in output
        assert x.exit_code == 1

    # ********** Check verbosity level 0
    # redirect output to string so we can analyze it
    x = MyApplication("dummy", "Help.")
    oldarg = sys.argv
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    sys.argv = ("test_Application.py").split()
    try:
        x.run()
    finally:
        output = sys.stdout.getvalue()
        sys.argv = oldarg
        sys.stdout = old_stdout
        assert the_verbose_0_msg in output
        assert the_verbose_1_msg not in output

    # ********** Check verbosity level 1
    # redirect output to string so we can analyze it
    x = MyApplication("dummy", "Help.")
    oldarg = sys.argv
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    sys.argv = ("test_Application.py -v").split()
    try:
        x.run()
    finally:
        output = sys.stdout.getvalue()
        sys.argv = oldarg
        sys.stdout = old_stdout
        assert the_verbose_0_msg in output
        assert the_verbose_1_msg in output

    # ********** Check version (wrapper class redirects helper files to src/test)
    # redirect output to string so we can analyze it
    x = MyApplication("dummy", "Help.")
    oldarg = sys.argv
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    sys.argv = ("test_Application.py --version").split()
    try:
        x.run()
    finally:
        output = sys.stdout.getvalue()
        sys.argv = oldarg
        sys.stdout = old_stdout
        # contents of file src/test/test_Application.py
        assert "Version: v0.0.0 initial-28-gd96431b" in output

    # ********** We are not an app registered via add_msc_app_python(). Therefore --version should fail (simulating a partly installation)
    # redirect output to string so we can analyze it
    x = MyApplication("dummy", "Help.", use_test_helper_file_directory=False)
    oldarg = sys.argv
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    sys.argv = ("test_Application.py --version").split()
    try:
        assert x.exit_code == 0
        rc = x.run()
        assert x.exit_code == 1
    finally:
        output = sys.stderr.getvalue()
        sys.argv = oldarg
        sys.stderr = old_stderr
        # contents of file src/test/test_Application.py
        assert "Helper file for 'version' not found" in output

    # ********** Check copyright (wrapper class redirects helper files to src/test)
    # redirect output to string so we can analyze it
    x = MyApplication("dummy", "Help.")
    oldarg = sys.argv
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    sys.argv = ("test_Application.py --copyright").split()
    try:
        assert x.exit_code == 0
        x.run()
        assert x.exit_code == 1
    finally:
        output = sys.stdout.getvalue()
        sys.argv = oldarg
        sys.stdout = old_stdout
        # contents of file src/test/test_Application.py
        assert "Copyright (C)" in output


if __name__ == "__main__":
    test_CompliantArgumentParser()
    test_UsageException()
    test_Application()
