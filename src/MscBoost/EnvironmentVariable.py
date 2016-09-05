import os
import weakref

class EnvironmentVariable():
    """Provides environment variables that will be printed by Application's --help.
    """

    _variables = {}

    ## @param name Name of the environment variable
    ## @param help Help text of the environment variable.
    ## @param default_value The default value of the variable if it has not been defined yet.
    def __init__(self, name, help, default_value=None):
        """Creates a new environment variable. It is automatically registered and removed when no longer referenced"""
        # We need to assign variables first before doing assertion, otherwise __del__ might fail using these variables
        ##  Name of the environment variable (printenv)
        self.name = name
        ## Help text for Application's --help
        self.help = help
        ## Default value that is used when this environment variable is not set
        self.default_value = default_value
        EnvironmentVariable._variables[self.name] = weakref.ref(self)

        # Some compliance checks
        assert len(name) > 0, "Name must be set"
        assert len(help) > 0, "Help must be set"
        assert help[0].isupper(), "Help must start with a capital letter"
        assert help.endswith('.'), "Help must end with a ."

    def __repr__(self):
        return "<EnvironmentVariable %s == '%s'>" % (self.name, self.get_value())

    def __del__(self):
        """Automatically removes the environment variable from the list returned by get_all_variables_sorted()"""
        try:
            del EnvironmentVariable._variables[self.name]
        except:  # pragma: no cover
            pass

    def clear():
        """Clears all environment variables"""
        EnvironmentVariable._variables = {}

    ## @return the value of the environment variable or a default value if the variable does not exist.
    def get_value(self, default=None):
        """
        Returns the value of the environment variable or a default value if it does not exist.
        When the parameter default is not None use it as default_value, otherwise use self.default_value.
        """
        if default is not None:
            default_value = default
        else:
            default_value = self.default_value
        return os.environ.get(self.name, default_value)

    ## @return iterator to a sorted list of weak references of all existing EnvironmentVariable
    def get_all_variables_sorted():
        """Returns a sorted iterator of weak references to all EnvironmentVariables"""
        return iter(sorted(EnvironmentVariable._variables.values(), key=EnvironmentVariable._name))

    @staticmethod
    ## @param that Weak reference to environment variable
    def _name(that):
        """Returns the name of that"""
        return that().name
