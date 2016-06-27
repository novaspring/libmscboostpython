import os
import weakref

class EnvironmentVariable():
    """Provides environment variables that will be printed by Application's --help.
    """

    _variables = {}

    ## @param name Name of the environment variable
    ## @param help Help text of the environment variable.
    def __init__(self, name, help):
        """Creates a new environment variable. It is automatically registered and removed when no longer referenced"""
        # We need to assign variables first before doing assertion, otherwise __del__ might fail using these variables
        ##  Name of the environment variable (printenv)
        self.name = name
        ## Help text for Application's --help
        self.help = help
        EnvironmentVariable._variables[self.name] = weakref.ref(self)

        # Some compliance checks
        assert len(name) > 0, "Name must be set"
        assert len(help) > 0, "Help must be set"
        assert help[0].isupper(), "Help must start with a capital letter"
        assert help.endswith('.'), "Help must end with a ."

    def __del__(self):
        """Automatically removes the environment variable from the list returned by get_all_variables_sorted()"""
        del EnvironmentVariable._variables[self.name]

    ## @return None if the variable does not exist.
    def get_value(self):
        """Returns the value of the environment variable or none if it does not exists."""
        return os.environ.get(self.name)

    ## @return iterator to a sorted list of weak references of all existing EnvironmentVariable
    def get_all_variables_sorted():
        """Returns a sorted iterator of weak references to all EnvironmentVariables"""
        return iter(sorted(EnvironmentVariable._variables.values(), key=EnvironmentVariable._name))

    @staticmethod
    ## @param that Weak reference to environment variable
    def _name(that):
        """Returns the name of that"""
        return that().name
    