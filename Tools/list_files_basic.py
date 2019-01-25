from gc import collect
import os
# noinspection PyUnresolvedReferences
import uos
print('--[LOCAL FILES]----------------------------')
# noinspection PyArgumentList
files = [f for f in os.listdir()]
files.sort()
for file in files:
    s = uos.stat(file)
    print('{: <35}  {: >6}'.format(file, s[6]))
print('-------------------------------------------')

from sys import modules
if __name__ in modules:
    del modules[__name__]
