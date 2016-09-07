import argparse

from .UsageException import UsageException
from .FindBestMatch import FindBestMatch

class _CompliantArgumentParser(argparse.ArgumentParser):
    """Enhanced argument parser that performes compliance checks on --help and returns best fitting arguments."""
    def __init__(self, *args, **kwargs):
        kwargs["add_help"] = False  # Handled directly by application. We force it so subparses borrow this behaviour.
        self._subparser_cmd = None
        super().__init__(*args, **kwargs)

    def add_argument(self, *args, **kwargs):
        """
        add_argument(dest, ..., name=value, ...)
        add_argument(option_string, option_string, ..., name=value, ...)
        """
        arg = args[0]
        help_text = ""

        if kwargs:
            for key, value in kwargs.items():
                if key == "help":
                    help_text = value

                    # Some compliance checks
                    assert len(help_text) > 0, "{}: Help for must be set".format(arg)
                    assert help_text[0].isupper(), "{}: Help must start with a capital letter".format(arg)
                    assert help_text.endswith('.'), "{}: Help must end with a .".format(arg)

        assert len(help_text) > 0, "{}: Help must be present".format(arg)

        super().add_argument(*args, **kwargs)

    def add_subparsers(self, **kwargs):
        kwargs.setdefault("dest", "sub_parser_command")
        self._subparser_cmd = kwargs["dest"]

        subparsers = super().add_subparsers(**kwargs)
        self._subparsers = subparsers
        return subparsers

    def parse_args(self, args=None, namespace=None):
        """If an argument on the command line is not known, the nearest match is reported."""
        args, argv = self.parse_known_args(args, namespace)
        if argv:
            arg = argv[0]
            msg = "Unknown command line option '{0}' - did you mean '{1}'?".format(
                      arg,
                      self._find_best_next_argument(arg),
                      )

            self.error(msg)
        if self._subparser_cmd is not None:
            # When a subparser is specified and no action is given on the command line: show an error message
            specified_subparser_cmd = args.__dict__[self._subparser_cmd]
            if specified_subparser_cmd is None:
                possible_subcommands = list(self._subparsers.choices.keys())
                if not(any([args.copyright, args.version, args.help])):
                    self.error("No command line action given - choose from: %s" % ", ".join(possible_subcommands))
        return args

    def _check_value(self, action, value):
        # Override the base class implementation to show the best match for the given command line action
        # The original implementation would show all available command line actions
        if action.choices is not None and value not in action.choices:
            possible_subcommands = list(self._subparsers.choices.keys())
            msg = "Unknown command line action '{0}' - did you mean '{1}'?".format(
                      value,
                      FindBestMatch(value, possible_subcommands),
                      )
            self.error(msg)

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

    ## @brief Generates a help text. Unlike the base method in argparse, we print
    ## the help text of the sub-arguments, too.
    ## in argparse, you have to do "app command --help" to get the arguments of "command". With CompliantParser, "app --help" is sufficient.
    ## The default behaviour is is not useful as we want to provide one help documentation containing everything (on our buildserver).
    ## @return the formatted help text
    def format_help(self):
        """Generates a help text for this argument parser."""
        formatter = self._get_formatter()

        # usage
        formatter.add_usage(self.usage, self._actions,
                            self._mutually_exclusive_groups)

        # description
        formatter.add_text(self.description)

        # positionals, optionals and user-defined groups
        for action_group in self._action_groups:
            formatter.start_section(action_group.title)
            formatter.add_text(action_group.description)
            formatter.add_arguments(action_group._group_actions)
            formatter.end_section()

            # Print the (sub)arguments of the sub-parser. This overwrites base method behaviour.
            for a in action_group._group_actions:
                if isinstance(a, argparse._SubParsersAction):
                    for n in a._name_parser_map:
                        formatter.start_section("sub-arguments of \"{0}\"".format(n))
                        p = a._name_parser_map[n]

                        for actions in p._actions:
                            formatter.add_argument(actions)
                        formatter.end_section()

        # epilog
        formatter.add_text(self.epilog)

        # determine help from format above
        return formatter.format_help()
