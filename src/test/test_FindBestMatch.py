from MscBoost.FindBestMatch import FindBestMatch

def test_FindBestMatch():
    apple = "apple"
    cherry = "cherry"
    tomato = "tomato"

    haystack = [apple, cherry, tomato]

    assert FindBestMatch(apple + "wine", haystack) == apple
    assert FindBestMatch("tomata", haystack) == tomato
    assert FindBestMatch("chilly", haystack) == cherry
    assert FindBestMatch("tom", haystack) == tomato
    assert FindBestMatch("tom", []) is None
    assert FindBestMatch("tom", [""]) == ""
