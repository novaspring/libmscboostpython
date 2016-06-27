import MscBoost

def test_FindBestMatch():
    apple = "apple"
    cherry = "cherry"
    tomato = "tomato"

    haystack = [apple, cherry, tomato]

    assert MscBoost.FindBestMatch(apple + "wine", haystack) == apple
    assert MscBoost.FindBestMatch("tomata", haystack) == tomato
    assert MscBoost.FindBestMatch("chilly", haystack) == cherry
    assert MscBoost.FindBestMatch("tom", haystack) == tomato
    assert MscBoost.FindBestMatch("tom", []) is None
    assert MscBoost.FindBestMatch("tom", [""]) == ""

if __name__ == "__main__":
    test_FindBestMatch()
