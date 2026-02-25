# Ввод чисел
nums = list(map(int, input().split()))

# Лямбда для проверки простого числа
is_prime = lambda n: n > 1 and all(n % i != 0 for i in range(2, int(n**0.5)+1))

# Фильтруем простые числа
primes = list(filter(is_prime, nums))

# Вывод
if primes:
    print(*primes)
else:
    print("No primes")
