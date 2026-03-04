import re
s=input()
match = re.search(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', s)

if match:
    print(match.group())
else:
    print("No email")