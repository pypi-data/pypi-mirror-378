# İnceses - Turkish Phonetic Transcriptor


*  The phonetic transcriptor function was first written for the [İncesöz](https://github.com/enistuna/incesoz_turkish_linguistics_analyzer) project in 2024 and is now being used for its own Python package for easier deployment and usability.
The function was first developed using the **Özgün Koşaner's** lecture notes from the Phonetics class at *Dokuz Eylul University's Linguistics* department.

## Explanation ##
* To use it, simply import the Python package and write the "inceses.phonetic_analysis('')" line of code. 
Finally, put the Turkish word you want to transcript in the quotation marks and run the code

## Installation ##
* To use the Turkish phonetic transciptor, first install the Python package using the pip command.
```
pip install inceses
```

## How to Use ##
```py
import inceses

decipher = inceses.phonetic_analysis('Enis Tuna ile yemeğe mi gittin?')

print(decipher)
>> "[ ɛnis tʰunα ile jɛme•e mi ɟittʰin? ]"
```