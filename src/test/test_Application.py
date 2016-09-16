import io
import os
import signal
import subprocess
import sys
import time

import pytest

from MscBoost.Application import _CompliantArgumentParser
from MscBoost.Application import Application
from MscBoost.Application import TerminationHandler
from MscBoost.EnvironmentVariable import EnvironmentVariable
from MscBoost.Logging import Log
from MscBoost.UsageException import UsageException
from MscBoost.MscProject import MscProject

the_main_exception_message = "as requested"
the_verbose_0_msg = "verbose0"
the_verbose_1_msg = "verbose1"

class MyApplication(Application):
    def __init__(self,
                 name="App",
                 short_help="Help.",
                 main_will_fail=False,
                 use_test_helper_file_directory=True,
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
            search_dirs = [os.path.join(MscProject.find_project_root(os.getcwd()), "src", "test")]
        else:
            search_dirs = []

        return search_dirs

def test_UsageException():
    msg = "What"
    e = UsageException(msg)
    assert str(e) == msg
    assert isinstance(e, Exception)

def test_CompliantArgumentParser():
    parser = _CompliantArgumentParser(
        prog="dummy",
        add_help=False,
    )

    # Test compliant arguments
    with pytest.raises(AssertionError):
        parser.add_argument("-v", help="")  # no help is an error
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
    assert args.store

    store_cmdline_arg_t = store_cmdline_arg + "t"
    try:
        parser.parse_args(store_cmdline_arg_t.split())
    except UsageException as e:
        msg = str(e)
        expected = "Unknown command line option '" + store_cmdline_arg_t + "' - did you mean '" + store_cmdline_arg + "'?"
        assert expected == msg

def test_CompliantArgumentParser_subarguments():
    parser = _CompliantArgumentParser(
        prog="dummy",
        add_help=False,
    )
    parser.add_argument("--dummy", action="store_true", help="Dummy.")
    parser.add_argument("--copyright", action="store_true", help="Copyright.")
    parser.add_argument("--version", action="store_true", help="Version.")
    parser.add_argument("--help", action="store_true", help="Help.")
    with pytest.raises(AssertionError):
        parser.add_argument("--missing-help")

    sub_parsers = parser.add_subparsers(title="commands", help="Commands.")
    cmd_parser = sub_parsers.add_parser("clone", help="Clones.")
    cmd_parser = sub_parsers.add_parser("update", help="Updates.")
    cmd_parser.add_argument("--from",
                            help="From.",
                            action="store_true")

    # Test that subarguments are printed in help.
    help = parser.format_help()
    assert "commands:" in help
    assert "clone" in help
    assert "update" in help
    assert "sub-arguments of \"update\"" in help
    assert "--from" in help

    # No command line action is given, but --help or --copyright or --version is specified -> all o.k.
    for cmdline_arg in ("--help", "--copyright", "--version"):
        parser.parse_args(cmdline_arg.split())

    # No command line action given -> an error must be raised
    for cmdline_arg in ("", "--dummy"):
        try:
            parser.parse_args(cmdline_arg.split())
        except UsageException as e:
            msg = str(e)
            expected = "No command line action given - choose from: clone, update"
            assert expected == msg

    # Invoke the command line action clone
    cmdline_arg = "clone"
    args = parser.parse_args(cmdline_arg.split())
    assert args.sub_parser_command == cmdline_arg

    # A wrong command line command is given -> show the best match
    cmdline_arg = "close"
    try:
        parser.parse_args(cmdline_arg.split())
    except UsageException as e:
        msg = str(e)
        expected = "Unknown command line action '%s' - did you mean 'clone'?" % cmdline_arg
        assert expected == msg

def test_Application():
    # Compliance checks
    with pytest.raises(AssertionError):
        x = MyApplication("", "Help.")  # no name is an error

    with pytest.raises(AssertionError):
        MyApplication("name", "")  # no help is an error

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
        expected = "Unknown command line option '{0}' - did you mean '{1}'?".format(
            non_existing_arg,
            existing_arg
            )
        assert expected in output
        assert x.exit_code == 1

    # ********** Ensure that error exceptions are handled.
    # redirect output to string so we can analyze it
    x = MyApplication("dummy", "Help.", main_will_fail=True)
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
        x.run()
        assert x.exit_code == 1
    finally:
        output = sys.stderr.getvalue()
        sys.argv = oldarg
        sys.stderr = old_stderr
        # contents of file src/test/test_Application.py
        assert "Helper file 'test_Application.py.version' for 'version' not found" in output

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

def test_termination_handler(docker_test_active, msc_boost_python_dir):
    test_prg = """
import os
import time
from MscBoost.Application import TerminationHandler
t = TerminationHandler()
print("PID: %s" % os.getpid(), flush=True)
for i in range(20):
    time.sleep(0.1)
    if t.terminate:
        print("Signal: %s" % t.signum, flush=True)
        break
if not t.terminate:
   print("Didn't catch a signal", flush=True)
"""
    signal_list = (signal.SIGTERM, signal.SIGINT)
    if not docker_test_active:
        test_prg_file_name = os.path.abspath("test-termination-handler")
        with open(test_prg_file_name, "w") as f:
            f.write(test_prg)
        for signal_nr in signal_list:
            cmd = "PYTHONPATH=%s python3 %s" % (msc_boost_python_dir, test_prg_file_name)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            subprocess_pid = p.stdout.readline().decode("ascii").strip()
            assert subprocess_pid == "PID: %d" % p.pid
            p.send_signal(signal_nr)
            p.wait()
            caught_signal = p.stdout.readline().decode("ascii").strip()
            assert caught_signal == "Signal: %d" % signal_nr
        os.unlink(test_prg_file_name)

    current_signal_handlers = {}
    for signal_nr in signal_list:
        current_signal_handlers[signal_nr] = signal.getsignal(signal_nr)
    t = TerminationHandler()
    assert t.signum is None
    assert not t.terminate
    os.system("kill -s TERM %d" % os.getpid())
    for i in range(20):
        time.sleep(0.1)
        if t.terminate:
            break
    assert t.terminate
    assert t.signum == signal.SIGTERM
    for signal_nr in signal_list:
        signal.signal(signal_nr, current_signal_handlers[signal_nr])
