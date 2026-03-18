import os

# Создание папок
os.mkdir("test_dir")
os.makedirs("parent/child/grandchild")

# Текущая директория
print(os.getcwd())

# Список файлов
print(os.listdir())

# Удаление папки
os.rmdir("test_dir")