import io
import Msc.Boost
import os
import pytest
import sys
import TestHelper

from Msc.Boost import MscProject

def test_Version():
    version_test_dir = os.path.join(TestHelper.find_project_root(), "src", "test", "Version")

    # good
    v = MscProject.Version(os.path.join(version_test_dir, "good"))
    assert str(v) == "v1.2.3.4"

    assert v.major == 1
    assert v.minor == 2
    assert v.patch == 3
    assert v.build == 4

    # build number is missing
    v = MscProject.Version(os.path.join(version_test_dir, "no_build"))
    assert str(v) == "v1.2.3"

    assert v.major == 1
    assert v.minor == 2
    assert v.patch == 3
    assert v.build == None

    # incomplete
    with pytest.raises(KeyError):
        v = MscProject.Version(os.path.join(version_test_dir, "incomplete"))

    # bad
    with pytest.raises(ValueError):
        v = MscProject.Version(os.path.join(version_test_dir, "bad"))

    # bad
    with pytest.raises(FileNotFoundError):
        v = MscProject.Version(os.path.join(version_test_dir, "empty"))

    version_test_dir = os.path.join(TestHelper.find_project_root(), "src", "test", "Version")

def test_MscProject():
    version_test_dir = os.path.join(TestHelper.find_project_root(), "src", "test", "Version")

    # good
    path = os.path.join(version_test_dir, "good")
    proj = MscProject.MscProject(path)
    assert proj.path == path
    assert str(proj.version) == "v1.2.3.4"
        
if __name__ == "__main__":
    test_Version()
    test_MscProject()
