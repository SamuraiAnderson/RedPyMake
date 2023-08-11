import os


print(os.stat('./Symbol.py').st_mtime)
print(int(os.stat('./Symbol.py').st_mtime))
a = 2
a = 3
