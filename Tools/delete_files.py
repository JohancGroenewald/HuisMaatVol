import sys
import os
import gc

exclude = [
    'crc16.py',
    'list_files.py',
    'reboot.py',
    'unload.py',
    'webrepl_cfg.py'
]
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
