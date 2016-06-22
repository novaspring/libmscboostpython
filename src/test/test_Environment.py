import os
import pytest

from MscBoost import EnvironmentVariable

def check_variable_count(count):
    i = 0
    for var in EnvironmentVariable.get_all_variables_sorted():
        i = i + 1
    assert i == count, str(count) + " variables stored instead of " + str(i)
    
def add_temporary_variable(count):
    nt = "test_Environment_temp"
    ht = "Temp."
    v = EnvironmentVariable(ht, ht)
    check_variable_count(count + 1)
    
def test_EnvironmentVariable():
    # No environment variables exist so far
    check_variable_count(0)

    # Compliance checks
    with pytest.raises(AssertionError):
        EnvironmentVariable("", "Help.") # no name is an error

    with pytest.raises(AssertionError):
        EnvironmentVariable("name", "") # no help is an error

    with pytest.raises(AssertionError):
        EnvironmentVariable("name", "help must start capitalized.")

    with pytest.raises(AssertionError):
        EnvironmentVariable("name", "Help must end with '.'")

    check_variable_count(0)

    # Register one variable
    
    n1 = "test_Environment_s1"
    h1 = "Help1."
    v1 = EnvironmentVariable(n1, h1)

    assert n1 == v1.name
    assert h1 == v1.help
    check_variable_count(1)

    # Check the environment variable returned value
    s1 = "bla"
    os.environ[n1] = s1
    assert s1 == v1.get_value()
    
    # Add a temporary variable that has been removed when the function returns
    add_temporary_variable(1)
    check_variable_count(1)

    # Register another variable
    # is added before v2
    n3 = "test_Environment_s3"
    h3 = "Help3."
    v3 = EnvironmentVariable(n3, h3)
    check_variable_count(2)

    # Register another variable, it will be sorted before v2
    n2 = "test_Environment_s2"
    h2 = "Help2."
    v2 = EnvironmentVariable(n2, h2)
    check_variable_count(3)

    # Ensure that all variables are returned sorted
    var_iter = EnvironmentVariable.get_all_variables_sorted()
    v = next(var_iter)
    assert v() == v1, "v1"
    v = next(var_iter)
    assert v() == v2, "v2"
    v = next(var_iter)
    assert v() == v3, "v3"
    with pytest.raises(StopIteration):
        v = next(var_iter)

    # Check dereferencing
    del v3
    v3 = None
    check_variable_count(2)
    var_iter = EnvironmentVariable.get_all_variables_sorted()
    v = next(var_iter)
    assert v() == v1, "v1"
    v = next(var_iter)
    assert v() == v2, "v2"
    with pytest.raises(StopIteration):
        v = next(var_iter)
    
if __name__ == "__main__":
    test_EnvironmentVariable()
