n = int(input())
arr = list(map(int, input().split()))

seen = set()
c=0
for i in range(0, n):
    seen.add(arr[i])
    print(seen, end=" ")
    print(i)

