import os

exclude = [
    'webrepl_cfg.py',
    'boot.py',
]
files = [f for f in os.listdir()]
files.sort()
for f in files:
    if f in exclude:
        print('Skipping ... {}'.format(f))
        continue
    print('Deleting ... {}'.format(f))
    os.remove(f)

# noinspection PyUnresolvedReferences
# import unload <-- Module has been cleaned so cant run it now!

import micropython
micropython.mem_info()

from sys import modules
if __name__ in modules:
    del modules[__name__]
