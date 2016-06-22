import argparse

from .UsageException import UsageException
from .FindBestMatch import FindBestMatch

class _CompliantArgumentParser(argparse.ArgumentParser):
    """Enhanced argument parser that performes compliance checks on --help and returns best fitting arguments."""
    def __init__(self, *args, **kwargs):
        super(self.__class__,self).__init__(*args, **kwargs)

    def add_argument(self, *args, **kwargs):
        """
        add_argument(dest, ..., name=value, ...)
        add_argument(option_string, option_string, ..., name=value, ...)
        """
        arg = args[0]
        help_text = ""

        if kwargs is not None:
            for key, value in kwargs.items():
                if key == "help":
                    help_text = value

                    # Some compliance checks
                    assert len(help_text) > 0, "{}: Help for must be set".format(arg)
                    assert help_text[0].isupper(), "{}: Help must start with a capital letter".format(arg)
                    assert help_text.endswith('.'), "{}: Help must end with a .".format(arg)

        assert len(help_text) > 0, "{}: Help must be present".format(arg)
            
        super(self.__class__,self).add_argument(*args, **kwargs)

    def parse_args(self, args=None, namespace=None):
        """If an argument on the command line is not known, the nearest match is reported."""
        args, argv = self.parse_known_args(args, namespace)
        if argv:
            arg = argv[0]
            msg = "Unknown command line option {0} - did you mean '{1}'?".format(
                      arg,
                      self._find_best_next_argument(arg),
                      )
                
            self.error(msg)
        return args
        
    def error(self, message):
        """Overrides default class to throw an exception instead of exiting"""
        raise UsageException(message)

    ## @param arg The argument for which the best available argument should be returned.
    ## @return The best next existing argument.
    def _find_best_next_argument(self, arg):
        known_arguments = []
        for action in self._actions:
            for option in action.option_strings:
                known_arguments.append(option)

        return FindBestMatch(arg, known_arguments)
