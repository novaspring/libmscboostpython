import os
import sys
import traceback

from abc import ABCMeta
from abc import abstractmethod

from .CompliantArgumentParser import _CompliantArgumentParser
from .EnvironmentVariable import EnvironmentVariable
from .Logging import GetLogger as Log
from .UsageException import UsageException

## @brief Main application.
## See also <a href="https://docs.python.org/3/howto/argparse.html">argparse</a>.
class Application():
    """Main application handling command line options and error handling. Override it, implement _Main() and call Run.
    Add arguments in constructor with self.ArgParser.add_argument().
    """
    _metaclass=ABCMeta

    ## @param name The application name, e.g. argv[0]
    ## @param short_help A short helptext printed with --help
    def __init__(self, name, short_help):
        # Some compliance checks
        assert len(name) > 0, "Name must be set"
        assert len(short_help) > 0, "Help must be set"
        assert short_help[0].isupper(), "Help must start with a capital letter"
        assert short_help.endswith('.'), "Help must end with a ."

        ## The command line name of the application.
        self.name = name
        ## A short helped printed at the head of the "--help" text.
        self.short_help = short_help

        ## Parser for arguments.
        self.arg_parser = _CompliantArgumentParser(
            prog = name,
            add_help = False, # We have our own help
            )

        self.arg_parser.add_argument("--copyright",
                                    action="store_true",
                                    help="Prints the copyright version and exits.")
        self.arg_parser.add_argument("-h", "--help",
                                    action="store_true",
                                    help="This help.")
        self.arg_parser.add_argument("-v", "--verbose",
                                    action="count",
                                    help="Increase verbosity level.",
                                    default=0)
        self.arg_parser.add_argument("--version",
                                    action="store_true",
                                    help="Prints the program version and exits.")

        ## Parsed arguments will be stored here.
        self.args = None

    ## @return The return code of Main().
    def run(self):
        """Evaluates command line arguments and calls Main and handling exceptions. Main must return 0 on success. Will exit on error via self._Exit()."""
        try:
            # Parse standard command line arguments
            self.args = self.arg_parser.parse_args()

            Log().set_verbosity(self.args.verbose)

            if self.args.help:
                self._print_usage_and_exit()

            if self.args.version:
                self._print_version()
            elif self.args.copyright:
                self._print_copyright()
            else:
                # Do the work.
                return self._main()
        except UsageException as e:
            self._print_usage_and_exit(str(e))
        except Exception as e:
            Log().error("*** ERROR: {0}".format(e) + "\n")
            Log().out(1, traceback.format_exc())

        self._exit(1)

    ## @param reasonMsg Message why usage is printed.
    def _print_usage_and_exit(self, reason_msg = None):
        """Prints the usage on the console and exits."""
        Log().out(0, self.short_help + "\n")
        self._print_version()
        Log().out(0, self.arg_parser.format_help() + "\n")
        Log().out(0, self._get_environment_variable_help() + "\n")

        examples = self._get_usage_examples()
        if examples != None:
            Log().out(0, "\nExamples:\n{0}\n".format(examples) + "\n")

        if reason_msg != None:
            Log().error(reason_msg + "\n")

        self._exit(2)

    ## @return A string with the help of the known EnvironmentVariable
    def _get_environment_variable_help(self):
        """Returns a help text for the known EnvironmentVariable."""
        rc = ""

        max_length = 0
        for env_var in EnvironmentVariable.get_all_variables_sorted():
            max_length = max(max_length, len(env_var().name))

        first = True
        for env_var in EnvironmentVariable.get_all_variables_sorted():
            if first:
                rc += "Using these environment variables:"
                first = False

            rc += "\n"

            rc += ("  {0:" + str(max_length) + "} : {1}").format(
                env_var().name,
                env_var().help,
                )

        return rc

    ## @return A string with the help of the known EnvironmentVariable
    def _get_usage_examples(self):
        """Returns the example help text for --help."""
        return ""

    ## @param exit_code The application exit code (0 on success, 1 on failure, 2 on command line issues)
    def _exit(self, exit_code):
        """Exits the application."""
        sys.exit(exit_code)

    def _print_version(self):
        """Prints the application version. The version is kept in a helper file (typically ./Release/<AppName>.version or /usr/share/MscApps/<AppName>.version.
         Installation and creation of the application version from version.in is done by CMake add_msc_app_python()"""
        version_file = self._get_helper_file("version")

        with open(version_file) as f:
            Log().out(0, "Version: {}\n".format(f.readline()))

    def _print_copyright(self):
        """Prints the copyright. The version is kept in a helper file (typically ./Release/<AppName>.copying or /usr/share/MscApps/<AppName>.copying.
         Installation and creation of the copyright from "COPYING_linked" or "COPYING" is done by CMake add_msc_app_python()"""
        copyright_file = self._get_helper_file("copying")

        with open(copyright_file) as f:
            Log().out(0, f.read())

    ## @return List with possible directories containing helper files.
    def _get_application_helper_file_search_directories(self):
        """Returns all directories which could contain a helper file, e.g. version or copyright. In C++ these information is linked into the application, in python we keep it in separate files."""
        search_dirs = []

        dir_of_app = os.path.dirname(sys.argv[0])

        # Might be called within the build directory.
        search_dirs.append (".")
        # Might be installed into rootfs.
        search_dirs.append("{}{}".format(dir_of_app, os.path.join("..", "MscApps")))

        return search_dirs

    ## @param type The helper file type, e.g. "version" or "copyright". Must be kept in sync with cmake add_msc_app_python.
    ## @return Returns the absolute path of the helper file or throws an exception if it doesn't exists.
    def _get_helper_file(self, type):
        """Returns the absolute path for the helper file of type 'type'"""
        app_file_name = os.path.basename(sys.argv[0])

        for dir in self._get_application_helper_file_search_directories():
            helper_file = os.path.join(dir,
                                      "{}.{}".format(
                                          app_file_name,
                                          type))
            if os.path.exists(helper_file):
                return helper_file

        raise Exception("Helper file for '{}' not found".format(type))
