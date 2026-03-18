import shutil
import os

# Копирование файла
shutil.copy("example.txt", "backup.txt")

# Удаление файла
if os.path.exists("backup.txt"):
    os.remove("backup.txt")
    print("File deleted")
else:
    print("File not found")