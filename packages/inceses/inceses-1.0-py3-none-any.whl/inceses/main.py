## İnceses - Turkish Phonetic Transcriptor
## by: Enis Tuna

"""
## İnceses - Turkish Phonetic Transcriptor

*  The phonetic transcriptor function was first written for the İncesöz project in 2024 and is now being used for its own 
Python package for easier deployment and usability. The function was first developed using the **Özgün Koşaner's** lecture notes from the Phonetics 
class at *Dokuz Eylul University's Linguistics* department.

### Explanation
* To use it, simply import the Python package and write the "inceses.phonetic_analysis('')" line of 
code. 
Finally, put the Turkish word you want to transcript in the quotation marks and run the code

### Usage
```
import inceses

decipher = inceses.phonetic_analysis('Enis Tuna ile yemeğe mi gittin?')

print(decipher)
>> "[ ɛnis tʰunα ile jɛme•e mi ɟittʰin? ]"
```
"""

import re


def phonetic_analysis(word):
    word = word.strip().lower()

    phonetic_map = {
        "c": "dʒ",
        "y": "j",
        "v": "ʋ",
        "a": "α",
        "ş": "ʃ",
        "ç": "tʃ",
        "j": "ʒ",
        "ı": "ɯ",
        "ü": "y",
        "ö": "ø",
    }

    analysis = "".join((phonetic_map.get(i, i) for i in word))

    allophone_rules = [
        (r"l(?=[αɯou])|(?<=[αɯou])l", "ɫ"),
        (r"g(?=[eiøy])|(?<=[eiøy])g", "ɟ"),
        (r"(?<=[αeɯioøuy])ğ(?=[αeɯioøuy])", "•"),
        (r"(?<=[^e])ğ", ": "),
        (r"eğ(?=[^αeɯioøuy])", "ej"),
        (r"h(?=[eiøy])", "ç"),
        (r"(?<=[αɯou])h", "x"),
        (r"ʋ(?=[uyoø])|(?<=[uyoø])ʋ", "β"),
        (r"f(?=[uyoø])|(?<=[uyoø])f", "ɸ"),
        (r"k(?=[αɯou])", "kʰ"),
        (r"k(?=[eiøy])", "cʰ"),
        (r"(?<=[eiøy])n(?=[cɟcʰ])", "ɲ"),
        (r"(?<=[αɯou])n(?=[kgkʰ])", "ŋ"),
        (r"m(?=[fɸ])", "ɱ"),
        (r"p(?=[αeɯioøuy])", "pʰ"),
        (r"t(?=[αeɯioøuy])", "tʰ"),
        (r"α(?=[mɱnŋɲ])", "α̃ "),
        (r"(?<=[ɟlcʰ])α(?=[ɟlcʰ])", "a"),
        (r"o(?=[mɱnŋɲrɾ̥lɫ])", "ɔ"),
        (r"ø(?=[mɱnŋɲrɾ̥lɫ])", "œ"),
        (r"e(?=[mɱnŋɲrɾ̥lɫ])", "ɛ"),
        (r"h$", "ç"),
        (r"r$", "ɾ̥"),
        (r"(?<=[eiøy])k$", "c"),
        (r"o$", "ɔ"),
        (r"ø$", "œ"),
    ]

    for pattern, replacement in allophone_rules:
        analysis = re.sub(pattern, replacement, analysis)

    return f"[ {analysis} ]"