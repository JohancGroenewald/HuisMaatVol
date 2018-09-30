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
import unload

import micropython
micropython.mem_info()
