import Msc.Boost
import pytest

def test_FindBestMatch():
    apple = "apple"
    cherry = "cherry"
    tomato = "tomato"

    haystack = [ apple, cherry, tomato ]

    assert Msc.Boost.FindBestMatch(apple + "wine", haystack) == apple
    assert Msc.Boost.FindBestMatch("tomata", haystack) == tomato
    assert Msc.Boost.FindBestMatch("chilly", haystack) == cherry
    assert Msc.Boost.FindBestMatch("tom", haystack) == tomato
    assert Msc.Boost.FindBestMatch("tom", []) == None
    assert Msc.Boost.FindBestMatch("tom", [ "" ]) == ""

if __name__ == "__main__":
    test_FindBestMatch()
