import pytest

from MscBoost import Version

def test_Version():
    major = 1
    minor = 2
    patch = 3
    build = 4

    # complete
    v = Version(major, minor, patch, build)
    assert v.major == major
    assert v.minor == minor
    assert v.patch == patch
    assert v.build == build

    # without build
    v = Version(major, minor, patch)
    assert v.major == major
    assert v.minor == minor
    assert v.patch == patch
    assert v.build == None

    # ==
    assert Version(1, 2, 3, 4) == Version(1, 2, 3, 4)
    assert Version(1, 2, 3) == Version (1, 2, 3, None)
    assert not Version(1, 2, 3) == None

    # !=
    assert Version(1, 2, 3) != None
    assert Version(1, 2, 3, 4) != Version (0, 2, 3, 4)
    assert Version(1, 2, 3, 4) != Version (1, 0, 3, 4)
    assert Version(1, 2, 3, 4) != Version (1, 2, 0, 4)
    assert Version(1, 2, 3, 4) != Version (1, 2, 3, 0)
    assert Version(1, 2, 3, 0) != Version (1, 2, 3, None)

    # <
    assert Version(0, 0, 0, 0) < Version(1, 0, 0, 0)
    assert Version(0, 0, 0, 0) < Version(0, 1, 0, 0)
    assert Version(0, 0, 0, 0) < Version(0, 0, 1, 0)
    assert Version(0, 0, 0, 0) < Version(0, 0, 0, 1)
    assert not Version(0, 0, 0, 0) < Version(0, 0, 0, None)
    assert Version(0, 0, 0, None) < Version(0, 0, 0, 1)
    assert not Version(0, 0, 0, None) < Version(0, 0, 0, None)
    assert Version(0, 0, 0, None) < Version(0, 0, 1, None)
    with pytest.raises(TypeError):
        assert not Version(0, 0, 0, 0) < ""

    # >
    assert Version(1, 0, 0, 0) > Version(0, 0, 0, 0)
    assert Version(0, 1, 0, 0) > Version(0, 0, 0, 0)
    assert Version(0, 0, 1, 0) > Version(0, 0, 0, 0)
    assert Version(0, 0, 0, 1) > Version(0, 0, 0, 0)
    assert not Version(0, 0, 0, None) > Version(0, 0, 0, 0)
    assert Version(0, 0, 0, 1) > Version(0, 0, 0, None)
    assert not Version(0, 0, 0, None) > Version(0, 0, 0, None)
    assert Version(0, 0, 1, None) > Version(0, 0, 0, None)

    # <=
    assert Version(0, 0, 0, 0) <= Version(1, 0, 0, 0)
    assert Version(1, 0, 0, 0) <= Version(1, 0, 0, 0)
    assert Version(0, 0, 0, 0) <= Version(0, 1, 0, 0)
    assert Version(0, 1, 0, 0) <= Version(0, 1, 0, 0)
    assert Version(0, 0, 0, 0) <= Version(0, 0, 1, 0)
    assert Version(0, 0, 1, 0) <= Version(0, 0, 1, 0)
    assert Version(0, 0, 0, 0) <= Version(0, 0, 0, 1)
    assert Version(0, 0, 0, 1) <= Version(0, 0, 0, 1)
    assert Version(0, 0, 0, 0) <= Version(0, 0, 0, None)
    assert Version(0, 0, 0, None) <= Version(0, 0, 0, 1)
    assert Version(0, 0, 0, None) <= Version(0, 0, 0, 0)
    assert Version(0, 0, 0, None) <= Version(0, 0, 1, None)
    with pytest.raises(TypeError):
        assert Version(0, 0, 0, 0) <= ""
    
    # >=
    assert Version(1, 0, 0, 0) >= Version(0, 0, 0, 0)
    assert Version(1, 0, 0, 0) >= Version(1, 0, 0, 0)
    assert Version(0, 1, 0, 0) >= Version(0, 0, 0, 0)
    assert Version(0, 1, 0, 0) >= Version(0, 1, 0, 0)
    assert Version(0, 0, 1, 0) >= Version(0, 0, 0, 0)
    assert Version(0, 0, 1, 0) >= Version(0, 0, 1, 0)
    assert Version(0, 0, 0, 1) >= Version(0, 0, 0, 0)
    assert Version(0, 0, 0, 1) >= Version(0, 0, 0, 1)
    assert Version(0, 0, 0, None) >= Version(0, 0, 0, 0)
    assert Version(0, 0, 0, 1) >= Version(0, 0, 0, None)
    assert Version(0, 0, 0, 0) >= Version(0, 0, 0, None)
    assert Version(0, 0, 1, None) >= Version(0, 0, 0, None)

if __name__ == "__main__":
    test_Version()
