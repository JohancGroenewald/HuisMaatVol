import sys
import os
import gc

exclude = ['webrepl_cfg.py', 'delete_files.py', 'unload.py', 'list_files.py']
files = [f for f in os.listdir()]
files.sort()
for f in files:
    if f in exclude:
        print('Skipping ... {}'.format(f))
        continue
    print('Deleting ... {}'.format(f))
    os.remove(f)

import unload

import micropython
micropython.mem_info()
