# Ввод массива
n = int(input())
arr = list(map(int, input().split()))

# Ввод операций
q = int(input())
operations = []

for _ in range(q):
    line = input().split()
    op = line[0]
    
    if op == "add":
        x = int(line[1])
        operations.append(lambda a, x=x: a + x)  # lambda с замыканием x
    elif op == "multiply":
        x = int(line[1])
        operations.append(lambda a, x=x: a * x)
    elif op == "power":
        x = int(line[1])
        operations.append(lambda a, x=x: a ** x)
    elif op == "abs":
        operations.append(lambda a: abs(a))

# Применяем операции к каждому элементу
result = arr[:]
for func in operations:
    result = list(map(func, result))

# Выводим результат
print(*result)
