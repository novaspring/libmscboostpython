import io
import Msc.Boost
import os
import pytest
import sys

from Msc.Boost.Application import _CompliantArgumentParser
from Msc.Boost.EnvironmentVariable import EnvironmentVariable
from Msc.Boost.UsageException import UsageException
from Msc.Boost.Logging import GetLogger as Log
from io import StringIO

mainExceptionMessage = "as requested"
verbose0Msg = "verbose0"
verbose1Msg = "verbose1"

class MyApplication(Msc.Boost.Application):
    def __init__(self,
                 name = "App",
                 shortHelp = "Help.",
                 mainWillFail = False,
                 useTestHelperFileDirectory = True,
    ):
        super(self.__class__, self).__init__(name, shortHelp)
        self.InMain = False
        self.InExit = False
        self.ExitCode = 0
        self.MainWillFail = mainWillFail
        self.UseTestHelperFileDirectory = useTestHelperFileDirectory

    def _Main(self):
        self.InMain = True
        if self.MainWillFail:
            raise Exception(mainExceptionMessage)
        Log().out(0, verbose0Msg)
        Log().out(1, verbose1Msg)

    def _Exit(self, exitCode):
        self.InExit = True
        self.ExitCode = exitCode

    def _GetApplicationHelperFileSearchDirectories(self):
        if self.UseTestHelperFileDirectory:
            dir = os.getcwd()
            while not os.path.exists(os.path.join(dir, "version.in")):
                dir = os.path.abspath(dir)
                if dir == "/":
                    # Reached root
                    raise Exception("Not called within cmake project directory")

                dir = os.path.join(dir, "..")

            searchDirs = [ os.path.join(dir, "src", "test") ]
        else:
            searchDirs = super(self.__class__, self)._GetApplicationHelperFileSearchDirectories()
            
        return searchDirs

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
    storeCmdlineArg = "--store"
    parser.add_argument(storeCmdlineArg, action="store_true", help="Help.")
    # test empty list not failing
    parser.parse_args("".split())
    args = parser.parse_args(storeCmdlineArg.split())
    assert args.store == True

    storeCmdlineArgT = storeCmdlineArg + "t"
    try:
        parser.parse_args(storeCmdlineArgT.split())
    except Msc.Boost.UsageException as e:
        msg = str(e)
        expected = "Unknown command line option " + storeCmdlineArgT + " - did you mean '" + storeCmdlineArg + "'?"
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
    try:
        assert not x.InMain
        x.Run()
        assert x.InMain
        assert x.ExitCode == 0
    finally:
        sys.argv = oldarg

    # ********** Ensure that there is a help with exit code 2
    # redirect output to string so we can analyze it
    x = MyApplication("dummy", "Help.")

    # register an environment variable
    envDummyName = "DUMMY"
    envDummyHelp = "Dummy application."
    envDummy = EnvironmentVariable(envDummyName, envDummyHelp)

    assert not x.InExit
    assert x.ExitCode == 0
    oldarg = sys.argv
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    sys.argv = "test_Application.py --help".split()
    try:
        x.Run()
    finally:
        output = sys.stdout.getvalue()
        sys.argv = oldarg
        sys.stdout = old_stdout
        assert "usage: dummy" in output
        assert x.InExit
        assert x.ExitCode == 2

        # Ensure that environment variables are listed:
        assert envDummyName in output
        assert envDummyHelp in output
        del(envDummy)

    # ********** Ensure that suggestions are made on failure.
    # redirect output to string so we can analyze it
    x = MyApplication("dummy", "Help.")
    oldarg = sys.argv
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    existingArg = "--help"
    nonExistingArg = existingArg + "x"
    sys.argv = ("test_Application.py " + nonExistingArg).split()
    try:
        assert x.ExitCode == 0
        x.Run()
    finally:
        output = sys.stderr.getvalue()
        sys.argv = oldarg
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        expected = "Unknown command line option {0} - did you mean '{1}'?".format(
            nonExistingArg,
            existingArg
            )
        assert expected in output
        assert x.ExitCode == 1

    # ********** Ensure that error exceptions are handled.
    # redirect output to string so we can analyze it
    x = MyApplication("dummy", "Help.", mainWillFail = True)
    oldarg = sys.argv
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    sys.argv = ("test_Application.py").split()
    try:
        assert x.ExitCode == 0
        x.Run()
    finally:
        output = sys.stderr.getvalue()
        sys.argv = oldarg
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        expected = "*** ERROR: " + mainExceptionMessage
        assert expected in output
        assert x.ExitCode == 1

    # ********** Check verbosity level 0
    # redirect output to string so we can analyze it
    x = MyApplication("dummy", "Help.")
    oldarg = sys.argv
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    sys.argv = ("test_Application.py").split()
    try:
        x.Run()
    finally:
        output = sys.stdout.getvalue()
        sys.argv = oldarg
        sys.stdout = old_stdout
        assert verbose0Msg in output
        assert verbose1Msg not in output

    # ********** Check verbosity level 1
    # redirect output to string so we can analyze it
    x = MyApplication("dummy", "Help.")
    oldarg = sys.argv
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    sys.argv = ("test_Application.py -v").split()
    try:
        x.Run()
    finally:
        output = sys.stdout.getvalue()
        sys.argv = oldarg
        sys.stdout = old_stdout
        assert verbose0Msg in output
        assert verbose1Msg in output

    # ********** Check version (wrapper class redirects helper files to src/test)
    # redirect output to string so we can analyze it
    x = MyApplication("dummy", "Help.")
    oldarg = sys.argv
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    sys.argv = ("test_Application.py --version").split()
    try:
        x.Run()
    finally:
        output = sys.stdout.getvalue()
        sys.argv = oldarg
        sys.stdout = old_stdout
        # contents of file src/test/test_Application.py
        assert "Version: v0.0.0 initial-28-gd96431b" in output

    # ********** We are not an app registered via add_msc_app_python(). Therefore --version should fail (simulating a partly installation)
    # redirect output to string so we can analyze it
    x = MyApplication("dummy", "Help.", useTestHelperFileDirectory=False)
    oldarg = sys.argv
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()
    sys.argv = ("test_Application.py --version").split()
    try:
        assert x.ExitCode == 0
        rc = x.Run()
        assert x.ExitCode == 1
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
        assert x.ExitCode == 0
        x.Run()
        assert x.ExitCode == 1
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
