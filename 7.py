a=input()
res=""
for ch in a:
    if 'a' <= ch <='z':
        ch= chr(ord(ch)-32)
        res += ch
print(res)