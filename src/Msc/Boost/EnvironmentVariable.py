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
        # Some compliance checks
        assert len(name) > 0, "Name must be set"
        assert len(help) > 0, "Help must be set"
        assert help[0].isupper(), "Help must start with a capital letter"
        assert help.endswith('.'), "Help must end with a ."

        ##  Name of the environment variable (printenv)
        self.Name = name
        ## Help text for Application's --help
        self.Help = help

        EnvironmentVariable._variables[self.Name] = weakref.ref(self)

    def __del__(self):
        """Automatically removes the environment variable from the list returned by GetAllVariables()"""
        del EnvironmentVariable._variables[self.Name]

    ## @return None if the variable does not exist.
    def GetValue(self):
        """Returns the value of the environment variable or none if it does not exists."""
        return os.environ.get(self.Name)

    ## @return iterator to a sorted list of weak references of all existing EnvironmentVariable
    def GetAllVariablesSorted():
        """Returns a sorted iterator of weak references to all EnvironmentVariables"""
        return iter(sorted(EnvironmentVariable._variables.values(), key=EnvironmentVariable._Name))

    @staticmethod
    ## @param that Weak reference to environment variable
    def _Name(that):
        """Returns the name of that"""
        return that().Name
    
