import os
from sys import implementation

if implementation.name == 'micropython':
    from micropython import opt_level
    opt_level(3)
    print('opt_level: {}'.format(opt_level()))
    from gc import collect
    from json import loads
    # noinspection PyUnresolvedReferences
    from crc16 import crc16_stream
    collect()
else:
    from json import dumps
    # noinspection PyUnresolvedReferences
    from crc16 import crc16

check_sums = 'checksum.json'


def cpython():
    ignore = [
        '.git', '.gitignore', '.idea', '__pycache__', 'Tools', 'Argief'
    ]
    checksum_buffer = {}
    print('--[TOOLS]--------------------------------------------------')
    files = [f for f in os.listdir('tools')]
    files.sort()
    for file in files:
        if file in ignore:
            continue
        s = os.stat(os.path.join('tools', file))
        try:
            with open(os.path.join('tools', file), 'rb') as f:
                h = crc16(f.read())
                checksum_buffer[file] = h
            print('{: <35}  {: >6}  {: >4}'.format(file, h, s[6]))
        except:
            print('{: <35}   ERROR  {: >4}'.format(file, s[6]))

    print('--[APPLICATION]--------------------------------------------')
    files = [f for f in os.listdir()]
    files.sort()
    for file in files:
        if file in ignore:
            continue
        s = os.stat(file)
        try:
            with open(file, 'rb') as f:
                h = crc16(f.read())
                checksum_buffer[file] = h
            print('{: <35}  {: >6}  {: >4}'.format(file, h, s[6]))
        except:
            print('{: <35}   ERROR  {: >4}'.format(file, s[6]))
    url = check_sums
    with open(url, 'w') as f:
        f.write(dumps(checksum_buffer))


def micropython():
    collect()
    # noinspection PyUnresolvedReferences
    with open(check_sums) as f:
        checksum_buffer = loads(f.read())
    import uos
    listed = []
    print('--[TOOLS]--------------------------------------------------')
    tools = [
        'cat.py',
        'cleanup.py',
        'cleanup_full.py',
        'crc16.py',
        'device_id.py',
        'list_files.py',
        'list_modules.py',
        'mem_info.py',
        'reboot.py',
        'unload.py',
        'update.py'
    ]
    # noinspection PyArgumentList
    files = [f for f in os.listdir() if f in tools]
    files.sort()
    listed.extend(files)
    for file in files:
        s = uos.stat(file)
        try:
            with open(file, 'rb') as f:
                h = crc16_stream(f)
            re_h = checksum_buffer[file]
            print('{: <35}  {: >4}  {: >6} {: >6} {}'.format(
                file, s[6], h, re_h, 'OK' if h == re_h else 'FAILED'),
            )
        except:
            print('{: <35}   ERROR  {: >4}'.format(file, s[6]))

    print('--[APPLICATION]--------------------------------------------')
    application = [
        'application.py',
        'boot.py',
        'config_local.py',
        'config_sonoff_4ch_v2.py',
        'config_sonoff_basic.py',
        'config_sonoff_dual_r2.py',
        'config_sonoff_touch_t1_r2_us_v1_2gang.py',
        'config_sonoff_touch_t1_r2_us_v1_3gang.py',
        'delayed.py',
        'functions.py',
        'responsive.py',
        'shutdown.py',
        'umqtt_simple.py',
        'variables.py',
        'wrapper.py'
    ]
    # noinspection PyArgumentList
    files = [f for f in os.listdir() if f in application]
    files.sort()
    listed.extend(files)
    for file in files:
        s = uos.stat(file)
        try:
            with open(file, 'rb') as f:
                h = crc16_stream(f)
            re_h = checksum_buffer[file]
            print('{: <35}  {: >4}  {: >6} {: >6} {}'.format(
                file, s[6], h, re_h, 'OK' if h == re_h else 'FAILED'),
            )
        except:
            print('{: <35}   ERROR  {: >4}'.format(file, s[6]))

    print('--[UN GROUPED]---------------------------------------------')
    # noinspection PyArgumentList
    files = [f for f in os.listdir() if f not in listed]
    files.sort()
    for file in files:
        s = uos.stat(file)
        try:
            with open(file, 'rb') as f:
                h = crc16_stream(f)
            print('{: <35}  {: >6}  {: >4}'.format(file, h, s[6]))
        except:
            print('{: <35}   ERROR  {: >4}'.format(file, s[6]))

    from sys import modules
    if 'crc16' in modules:
        del modules['crc16']
    if __name__ in modules:
        del modules[__name__]
    collect()

print('--[IMPLEMENTATION]-----------------------------------------')
print('{}'.format(implementation.name))
if implementation.name == 'micropython':
    micropython()
else:
    cpython()
