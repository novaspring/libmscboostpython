import io
import MscBoost
import os
import pytest
import sys

def test_Version():
    version_test_dir = os.path.join(MscBoost.MscProject.find_project_root(os.getcwd()), "src", "test", "Version")

    # good
    v = MscBoost.Version(os.path.join(version_test_dir, "good"))
    assert str(v) == "v1.2.3.4"

    assert v.major == 1
    assert v.minor == 2
    assert v.patch == 3
    assert v.build == 4

    # build number is missing
    v = MscBoost.Version(os.path.join(version_test_dir, "no_build"))
    assert str(v) == "v1.2.3"

    assert v.major == 1
    assert v.minor == 2
    assert v.patch == 3
    assert v.build == None

    # incomplete
    with pytest.raises(KeyError):
        v = MscBoost.Version(os.path.join(version_test_dir, "incomplete"))

    # bad
    with pytest.raises(ValueError):
        v = MscBoost.Version(os.path.join(version_test_dir, "bad"))

    # bad
    with pytest.raises(FileNotFoundError):
        v = MscBoost.Version(os.path.join(version_test_dir, "empty"))

    version_test_dir = os.path.join(MscBoost.MscProject.find_project_root(os.getcwd()), "src", "test", "Version")

def test_MscProject_find_project_root():
    # Ensure that we can find cmake's PROJECT_SOURCE_DIR
    root = MscBoost.MscProject.find_project_root(os.getcwd())
    # make a check whether this really seems to be the root of a cmake project
    assert os.path.exists(os.path.join(root, "COPYING"))
    assert os.path.exists(os.path.join(root, "README.txt"))
    assert os.path.exists(os.path.join(root, "CMakeLists.txt"))
    assert os.path.exists(os.path.join(root, ".gitignore"))
    assert os.path.exists(os.path.join(root, "version.in"))

    # There are typically no cmake projects unpacked as /tmp
    with pytest.raises(RuntimeError):
        MscBoost.MscProject.find_project_root("/tmp")

def test_MscProject():
    version_test_dir = os.path.join(MscBoost.MscProject.find_project_root(os.getcwd()), "src", "test", "Version")

    # good
    path = os.path.join(version_test_dir, "good")
    proj = MscBoost.MscProject(path)
    assert proj.path == path
    assert str(proj.version) == "v1.2.3.4"

if __name__ == "__main__":
    test_MscProject_find_project_root()
    test_Version()
    test_MscProject()
