import re

text = input()

digits = re.findall(r"\d", text)
print(*digits)