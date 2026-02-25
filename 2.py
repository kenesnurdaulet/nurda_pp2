n = int(input())

from collections import Counter

nums = []
for _ in range(n):
    nums.append(input().strip())

cnt = Counter(nums)

ans = 0
for k in cnt:
    if cnt[k] == 3:
        ans += 1

print(ans)
