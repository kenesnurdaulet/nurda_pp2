# Чтение файла

with open("example.txt", "r") as f:
    print(f.read())  # весь файл

with open("example.txt", "r") as f:
    print(f.readline())  # одна строка

with open("example.txt", "r") as f:
    print(f.readlines())  # список строк