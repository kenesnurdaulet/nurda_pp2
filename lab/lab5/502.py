import re
text=input()
word=input()
if re.search(word, text):
        print("Yes")
else:
        print("No")

 