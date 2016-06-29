import MscBoost
import os
import pytest

def test_MscProject_version():
    version_test_dir = os.path.join(MscBoost.MscProject.find_project_root(os.getcwd()), "src", "test", "Version")

    # good
    v = MscBoost.MscProject(os.path.join(version_test_dir, "good")).version
    assert str(v) == "v1.2.3.4"

    # extra number is missing
    v = MscBoost.MscProject(os.path.join(version_test_dir, "no_extra")).version
    assert str(v) == "v1.2.3"

    # incomplete
    with pytest.raises(KeyError):
        v = MscBoost.MscProject(os.path.join(version_test_dir, "incomplete")).version

    # bad
    with pytest.raises(ValueError):
        v = MscBoost.MscProject(os.path.join(version_test_dir, "bad")).version

    # empty
    with pytest.raises(FileNotFoundError):
        v = MscBoost.MscProject(os.path.join(version_test_dir, "empty")).version

    # comment
    v = MscBoost.MscProject(os.path.join(version_test_dir, "comment")).version
    assert str(v) == "v1.2.3.4"

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
