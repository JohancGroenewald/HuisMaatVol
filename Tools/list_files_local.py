import os
# noinspection PyUnresolvedReferences
from crc16 import crc16

ignore = [
    '.git', '.gitignore', '.idea', '__pycache__', 'Tools', 'Argief'
]

print('--[TOOLS]----------------------------------------------')
files = [f for f in os.listdir('tools')]
files.sort()
for file in files:
    if file in ignore:
        continue
    s = os.stat(os.path.join('tools', file))
    try:
        with open(os.path.join('tools', file), 'rb') as f:
            h = crc16(f.read())
        print('{: <25}  {: >6}  {: >4}'.format(file, h, s[6]))
    except:
        print('{: <25}   ERROR  {: >4}'.format(file, s[6]))

print('--[APPLICATION]----------------------------------------')
files = [f for f in os.listdir()]
files.sort()
for file in files:
    if file in ignore:
        continue
    s = os.stat(file)
    try:
        with open(file, 'rb') as f:
            h = crc16(f.read())
        print('{: <25}  {: >6}  {: >4}'.format(file, h, s[6]))
    except:
        print('{: <25}   ERROR  {: >4}'.format(file, s[6]))
