import sys

from abc import ABCMeta
from abc import abstractmethod

from .CompliantArgumentParser import _CompliantArgumentParser
from .EnvironmentVariable import *
from .Logging import GetLogger as Log
from .UsageException import *

class Application():
    """Main application handling command line options and error handling. Override it, implement _Main() and call Run
    """
    _metaclass=ABCMeta

    # @param name The application name, e.g. argv[0]
    # @param shortHelp A short helptext printed with --help
    def __init__(self, name, shortHelp):
        # Some compliance checks
        assert len(name) > 0, "Name must be set"
        assert len(shortHelp) > 0, "Help must be set"
        assert shortHelp[0].isupper(), "Help must start with a capital letter"
        assert shortHelp.endswith('.'), "Help must end with a ."

        ## The command line name of the application.
        self.Name = name
        ## A short helped printed at the head of the "--help" text.
        self.ShortHelp = shortHelp

        ## Parser for arguments.
        self.ArgParser = _CompliantArgumentParser(
            prog = name,
            add_help = False, # We have our own help
            )

        self.ArgParser.add_argument("-h", "--help", action="store_true", help="This help.")

        ## Parsed arguments will be stored here.
        self.Args = None

    # @return The return code of Main().
    def Run(self):
        """Evaluates command line arguments and calls Main and handling exceptions. Main must return 0 on success. Will exit on error via self._Exit()."""
        try:
            self.Args = self.ArgParser.parse_args()

            if self.Args.help:
                self._PrintUsageAndExit()

            return self._Main()
        except UsageException as e:
            self._PrintUsageAndExit(str(e))
        except Exception as e:
            Log().error("*** ERROR: {0}".format(e) + "\n")

        self._Exit(1)

    # @param reasonMsg Message why usage is printed.
    def _PrintUsageAndExit(self, reasonMsg = None):
        """Prints the usage on the console and exits."""
        Log().out(0, self.ShortHelp + "\n")
        Log().out(0, self.ArgParser.format_help() + "\n")
        Log().out(0, self._GetEnvironmentVariableHelp() + "\n")

        examples = self._GetUsageExamples()
        if examples != None:
            Log().out(0, "\nExamples:\n{0}\n".format(examples) + "\n")

        if reasonMsg != None:
            Log().error(reasonMsg + "\n")

        self._Exit(2)

    # @return A string with the help of the known EnvironmentVariable
    def _GetEnvironmentVariableHelp(self):
        """Returns a help text for the known EnvironmentVariable."""
        rc = ""

        maxLength = 0
        for envVar in EnvironmentVariable.GetAllVariablesSorted():
            maxLength = max(maxLength, len(envVar().Name))

        first = True
        for envVar in EnvironmentVariable.GetAllVariablesSorted():
            if first:
                rc += "Using these environment variables:"
                first = False

            rc += "\n"

            rc += ("  {0:" + str(maxLength) + "} : {1}").format(
                envVar().Name,
                envVar().Help,
                )

        return rc

    # @return A string with the help of the known EnvironmentVariable
    def _GetUsageExamples(self):
        """Returns the example help text for --help."""
        return ""

    # @param exitCode The application exit code (0 on success, 1 on failure, 2 on command line issues)
    def _Exit(self, exitCode):
        """Exits the application."""
        sys.exit(exitCode)
