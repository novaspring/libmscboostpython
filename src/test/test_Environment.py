import os
import pytest

from MscBoost import EnvironmentVariable

# Check initial environment
INITIAL_ENVIRONMENT_VARIABLE_LIST = ["MSC_FD3_IS_WARNING_PIPE", "MSC_LDK_GIT_SERVER"]

NUM_OF_INITIAL_ENVIRONMENT_VARIABLES = len(INITIAL_ENVIRONMENT_VARIABLE_LIST)

def check_variable_count(count):
    i = 0
    for var in EnvironmentVariable.get_all_variables_sorted():
        i = i + 1
    assert i == count, str(count) + " variables stored instead of " + str(i)

def add_temporary_variable(count):
    nt = "test_Environment_temp"
    ht = "Temp."
    v = EnvironmentVariable(nt, ht)
    check_variable_count(count + 1)
    assert v is not None  # This is a dummy test as we need to store EnvironmentVaraible so destructor is not callled to early. But pylama warns about unused varibles. So do something with it.

def test_EnvironmentVariable():
    check_variable_count(NUM_OF_INITIAL_ENVIRONMENT_VARIABLES)

    # Compliance checks
    with pytest.raises(AssertionError):
        EnvironmentVariable("", "Help.")  # no name is an error

    with pytest.raises(AssertionError):
        EnvironmentVariable("name", "")  # no help is an error

    with pytest.raises(AssertionError):
        EnvironmentVariable("name", "help must start capitalized.")

    with pytest.raises(AssertionError):
        EnvironmentVariable("name", "Help must end with '.'")

    check_variable_count(NUM_OF_INITIAL_ENVIRONMENT_VARIABLES)

    # Clear all environment variables
    EnvironmentVariable.clear()
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
    check_variable_count(2)
    var_iter = EnvironmentVariable.get_all_variables_sorted()
    v = next(var_iter)
    assert v() == v1, "v1"
    v = next(var_iter)
    assert v() == v2, "v2"
    with pytest.raises(StopIteration):
        v = next(var_iter)

def test_EnvironmentVariableDefault(monkeypatch):
    EnvironmentVariable.clear()
    v = EnvironmentVariable("ENV_TEST1", "Help1.", "default1")
    assert v.get_value() == "default1"
    assert v.get_value("mydefault1") == "mydefault1"
    monkeypatch.setenv("ENV_TEST1", "test1_val")
    assert v.get_value() == "test1_val"

if __name__ == "__main__":
    test_EnvironmentVariable()
