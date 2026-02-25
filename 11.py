# Родительский класс
class Person:
    def __init__(self, name):
        self.name = name

# Дочерний класс
class Student(Person):
    def __init__(self, name, gpa):
        super().__init__(name)  # вызываем конструктор родителя
        self.gpa = gpa

    def display(self):
        print(f"Student: {self.name}, GPA: {self.gpa}")

# Ввод данных
data = input().split()
name = data[0]
gpa = float(data[1])

# Создаём объект студента
student = Student(name, gpa)

# Выводим информацию
student.display()
