import sys

"""Implements finding the best string matching one in a list of other string using LevenshteinDistance.
I'm ashamed, but i wiki'd it.
https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
"""

def _levenshtein(s1, s2):
    if len(s1) < len(s2):
        return _levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

## @param needle The string to find in haystack
## @param haystack A list of strings
def FindBestMatch(needle, haystack):
    """Returns the string from haystack that matches needle best."""
    bestDistance = sys.maxsize
    bestMatch = None

    for entry in haystack:
        distance = _levenshtein(needle, entry)
        if (distance < bestDistance):
            bestDistance = distance
            bestMatch = entry

    return bestMatch
