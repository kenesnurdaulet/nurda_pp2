# Запись в файл

with open("example.txt", "w") as f:
    f.write("Hello\n")
    f.write("This is a file\n")

# Добавление (append)
with open("example.txt", "a") as f:
    f.write("New line added\n")