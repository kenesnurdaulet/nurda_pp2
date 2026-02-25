import math

class Circle:
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2

# Ввод радиуса
r = int(input())

# Создаём объект круга
c = Circle(r)

# Выводим площадь с 2 знаками после запятой
print(f"{c.area():.2f}")
