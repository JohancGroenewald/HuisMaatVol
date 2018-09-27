import os

exclude = [
    'cat.py',
    'cleanup.py',
    'crc16.py',
    'delete_files.py',
    'device_id.py',
    'list_files.py',
    'list_modules.py',
    'mem_info.py',
    'reboot.py',
    'unload.py',

    'webrepl_cfg.py',

    'application.py',
    'boot.py',
    # 'config_local.py',
    # 'config_sonoff_4ch_v2.py',
    # 'config_sonoff_basic.py',
    # 'config_sonoff_dual_r2.py',
    # 'config_sonoff_touch_t1_r2_us_v1_2gang.py',
    # 'config_sonoff_touch_t1_r2_us_v1_3gang.py',
    'delayed.py',
    'responsive.py',
    'umqtt_simple.py',
    'variables.py',
    'wrapper.py',
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
