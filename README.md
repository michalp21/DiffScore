# DiffScore

This script was created to compare ocr output against the original, but it can be used to compare pretty much any two text files. Conceptually, it is based on the program sclite, for comparing speech transcripts.

A quick explanation of the scoring:
* % Anchor is the percent of words that are exactly the same between ocr and original
* % Diff is the percent difference between ocr and original by character (normalized Levenshtein distance)

So you want a high % Anchor and a low % Diff.
