import shutil

# Перемещение файла
shutil.move("example.txt", "parent/example.txt")

# Копирование файла
shutil.copy("parent/example.txt", "copy_example.txt")