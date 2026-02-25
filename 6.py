codes = {
    "ZER": "0", "ONE": "1", "TWO": "2", "THR": "3", "FOU": "4",
    "FIV": "5", "SIX": "6", "SEV": "7", "EIG": "8", "NIN": "9"
}
rev ={v:k for k, v in codes.items()}

s = input().strip()

for i, ch in enumerate(s):
    if ch in "+-*":
        op=ch
        left=s[:i]
        right=s[i+1:]
        break
def decade(x):
    num=""
    for i in range(0,len(x),3):
        num += codes[x[i:i+3]]
    return int(num)

a=decade(left)
b=decade(right)
if op == "+":
    res=a+b
elif op== "-":
    res=a-b
else:
    res=a*b

out=""
for d in str(res):
    out += rev[d]

print(out)