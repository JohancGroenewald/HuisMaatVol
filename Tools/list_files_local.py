import os
from crc16 import crc16

files = [f for f in os.listdir()]
files.sort()
for file in files:
    if file in ['.git', '.gitignore', '.idea', '__pycache__']:
        continue
    s = os.stat(file)
    try:
        with open(file, 'rb') as f:
            h = crc16(f.read())
        print('{: <25}  {: >6}  {: >4}'.format(file, h, s[6]))
    except:
        print('{: <25}   ERROR  {: >4}'.format(file, s[6]))
