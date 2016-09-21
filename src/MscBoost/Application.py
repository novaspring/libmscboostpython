import os
import signal
import sys
import traceback

from .CompliantArgumentParser import _CompliantArgumentParser
from .EnvironmentVariable import EnvironmentVariable
from .Logging import Log
from .UsageException import UsageException
from .Util import get_timestamp_string

# MSC_APP_LOGGING holds a comma separated list of the following:
#   off         ... no logging
#   all         ... log everything
#   app-error   ... log application errors
#   usage-error ... log usage errors (traceback due to wrong command line parameters)
#   invocation  ... log every application invocation
MSC_APP_LOGGING = EnvironmentVariable("MSC_APP_LOGGING", "MSC Application logging (off|all|app-error|usage-error|invocation).", default_value="app-error")

## @brief Main application.
# See also <a href="https://docs.python.org/3/howto/argparse.html">argparse</a>.
class Application(object):
    """Main application handling command line options and error handling. Override it, implement _Main() and call Run.
    Add arguments in constructor with self.ArgParser.add_argument().
    """
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
                                                   prog=name,
                                                   )

        self.arg_parser.add_argument("--copyright",
                                     action="store_true",
                                     help="Prints the copyright version and exits.")
        self.arg_parser.add_argument("-h", "--help",
                                     action="store_true",
                                     help="This help and exits.")
        self.arg_parser.add_argument("-v", "--verbose",
                                     action="count",
                                     help="Increase verbosity level.",
                                     default=0)
        self.arg_parser.add_argument("--version",
                                     action="store_true",
                                     help="Prints the program version and exits.")

        ## Parsed arguments will be stored here.
        self.args = None

        self.app_startup_information = (get_timestamp_string(), os.getcwd(), sys.argv)
        self.invocation_logged = False
        self._setup_logging()
        if "invocation" in self.logging:
            self._log_invocation()

    def __repr__(self):
        return "<%s>" % self.__class__.__name__

    ## @return The return code of Main().
    def run(self):
        """Evaluates command line arguments and calls Main and handling exceptions. Main must return 0 on success. Will exit on error via self._Exit()."""
        log_to_log_file = False
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
            if "usage-error" in self.logging:
                log_to_log_file = True
                exception_msg = "%s\n%s" % (e, traceback.format_exc())
            self._print_usage_and_exit(str(e))
        except Exception as e:
            if "app-error" in self.logging:
                log_to_log_file = True
                exception_msg = "%s\n%s" % (e, traceback.format_exc())
            Log().error("*** ERROR: {0}".format(e))
            Log().out(1, traceback.format_exc())

        if log_to_log_file:
            self._log_invocation()
            log_file_name = self._get_logfile_name()
            start_time, cwd, args = self.app_startup_information
            with open(log_file_name, "a") as f:
                print("%s: ERROR: %s" % (get_timestamp_string(), exception_msg), file=f)
            Log().info("  See '%s' for error details" % log_file_name)
        self._exit(1)

    ## @param reasonMsg Message why usage is printed.
    def _print_usage_and_exit(self, reason_msg=None):
        """Prints the usage on the console and exits."""
        Log().out(0, self.short_help)
        self._print_version()
        Log().out(0, self.arg_parser.format_help())
        Log().out(0, self._get_environment_variable_help())

        examples = self._get_usage_examples()
        if examples is not None:
            Log().out(0, "\nExamples:\n{0}".format(examples))

        if reason_msg is not None:
            Log().error(reason_msg)

        self._exit(2)

    ## @return A string with the help of the known EnvironmentVariable
    def _get_environment_variable_help(self):
        """Returns a help text for the known EnvironmentVariable."""
        rc = ""

        max_length = max([len(v().name) for v in EnvironmentVariable.get_all_variables_sorted()])

        first = True
        for env_var in EnvironmentVariable.get_all_variables_sorted():
            if first:
                rc += "Using these environment variables:"
                first = False

            rc += "\n"

            help_txt = env_var().help
            if env_var().default_value is not None:
                help_txt += " <Default := '{}'>".format(env_var().default_value)
            rc += ("  {0:" + str(max_length) + "} : {1}").format(
                env_var().name,
                help_txt,
                )

        return rc

    ## @return A string with the help of the known EnvironmentVariable
    def _get_usage_examples(self):
        """Returns the example help text for --help."""
        return ""

    ## @param exit_code The application exit code (0 on success, 1 on failure, 2 on command line issues)
    def _exit(self, exit_code):
        """Exits the application."""
        sys.exit(exit_code)  # pragma: no cover

    def _print_version(self):
        """Prints the application version. The version is kept in a helper file (typically ./Release/<AppName>.version or /usr/share/MscApps/<AppName>.version.
         Installation and creation of the application version from version.in is done by CMake add_msc_app_python()"""
        version_file = self._get_helper_file("version")

        with open(version_file) as f:
            Log().out(0, "Version: {}".format(f.readline()))

    def _print_copyright(self):
        """Prints the copyright. The version is kept in a helper file (typically ./Release/<AppName>.copying or /usr/share/MscApps/<AppName>.copying.
         Installation and creation of the copyright from "COPYING_linked" or "COPYING" is done by CMake add_msc_app_python()"""
        copyright_file = self._get_helper_file("copying")

        with open(copyright_file) as f:
            Log().out(0, f.read())

    def _get_logfile_name(self):
        log_file_directory = os.path.join("/tmp/log", os.getenv("USER"))
        if not os.path.exists(log_file_directory):
            os.makedirs(log_file_directory)
        log_file_name = os.path.join(log_file_directory, "%s.log" % self.name)
        return log_file_name

    def _setup_logging(self):
        self.logging = [v.strip() for v in MSC_APP_LOGGING.get_value().split(",")]
        if "off" in self.logging:
            self.logging = ["off"]
        elif "all" in self.logging:
            for log_level in ["app-error", "usage-error", "invocation"]:
                if log_level not in self.logging:
                    self.logging.append(log_level)

    def _log_invocation(self, force=False):
        if self.invocation_logged and not force:
            return
        log_file_name = self._get_logfile_name()
        start_time, cwd, args = self.app_startup_information
        args = " ".join(args)
        with open(log_file_name, "a") as f:
            print("%s [%s]: %s" % (start_time, cwd, args), file=f)
        self.invocation_logged = True

    ## @return List with possible directories containing helper files.
    def _get_application_helper_file_search_directories(self):
        """Returns all directories which could contain a helper file, e.g. version or copyright. In C++ these information is linked into the application, in python we keep it in separate files."""
        search_dirs = []

        dir_of_app = os.path.dirname(os.path.realpath(sys.modules['__main__'].__file__))
        search_dirs.append(dir_of_app)

        # Might be called within the build directory.
        search_dirs.append(os.getcwd())
        # Might be installed into rootfs.
        search_dirs.append(os.path.abspath(os.path.join(dir_of_app, "..", "MscApps")))

        return search_dirs

    ## @param type The helper file type, e.g. "version" or "copyright". Must be kept in sync with cmake add_msc_app_python.
    ## @return Returns the absolute path of the helper file or throws an exception if it doesn't exist.
    def _get_helper_file(self, type):
        """Returns the absolute path for the helper file of type 'type'"""
        app_file_name = os.path.basename(sys.argv[0])

        helper_file_base_name = "%s.%s" % (app_file_name, type)
        for dir in self._get_application_helper_file_search_directories():
            helper_file = os.path.join(dir, helper_file_base_name)
            if os.path.exists(helper_file):
                return helper_file
        raise Exception("Helper file '{}' for '{}' not found".format(
            helper_file_base_name,
            type))

## @brief Handle SIGTERM, SIGINT
class TerminationHandler(object):
    def __init__(self):
        self.terminate = False
        self.signum = None
        signal.signal(signal.SIGTERM, self.handle_termination_signal)  # Receive SIGTERM
        signal.signal(signal.SIGINT, self.handle_termination_signal)   # Receive SIGINT or hit Ctrl-C

    def handle_termination_signal(self, signum, frame):
        self.signum = signum
        self.terminate = True
