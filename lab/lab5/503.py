import re

text = input()
word = input()

matches = re.findall(word, text)
print(len(matches))