n = int(input())
arr = list(map(int, input().split()))

mx = arr[0]
pos = 1

for i in range(1, n):
    if arr[i] > mx:
        mx = arr[i]
        pos = i + 1   # +1 because positions start from 1

print(pos)
