n = int(input())
arr = list(map(int, input().split()))

mx = arr[0]
mn = arr[0]

# find min and max
for i in range(1, n):
    if arr[i] < mn:
        mn = arr[i]
    if arr[i] > mx:
        mx = arr[i]

# replace all max with min
for i in range(n):
    if arr[i] == mx:
        arr[i] = mn

print(*arr)


# Считываем данные
n, l, r = map(int, input().split())
arr = list(map(int, input().split()))

# Переводим позиции из 1-based в 0-based
l -= 1
r -= 1

# Разворачиваем элементы с l до r
while l < r:
    arr[l], arr[r] = arr[r], arr[l]  # меняем местами
    l += 1  # двигаемся вправо
    r -= 1  # двигаемся влево

# Выводим результат
print(*arr)




n = int(input())

if n <= 1:
    print("No")
else:
    is_prime = True
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            is_prime = False
            break
    if is_prime:
        print("Yes")
    else:
        print("No")



from collections import Counter

# Read input
n = int(input())
arr = list(map(int, input().split()))

# Count frequencies
freq = Counter(arr)

# Find maximum frequency
max_count = max(freq.values())

# Find all elements with maximum frequency
candidates = [num for num, count in freq.items() if count == max_count]

# Output the smallest one
print(min(candidates))



n = int(input())

names = set()   # set stores only unique values

for _ in range(n):
    surname = input().strip()
    names.add(surname)

print(len(names))



n = int(input())
arr = list(map(int, input().split()))

seen = set()
c=0
for x in arr:
    if x in seen:
        c +=1
    else:
        c +=1
        seen.add(x)
