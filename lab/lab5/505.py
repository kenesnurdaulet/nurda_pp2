import re
s=input()

if re.match(r'^[A-Za-z].*\d$',s):
    print("Yes")
else:
    print("No")