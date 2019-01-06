import os
from json import dumps
# noinspection PyUnresolvedReferences
from crc16 import crc16


def cpython(check_sums):
    ignore = [
        '.git', '.gitignore', '.idea', '__pycache__', 'Tools', 'Argief', 'Evaluate'
    ]
    checksum_buffer = {}
    print('--[EVALUATE]-----------------------------------------------')
    files = [f for f in os.listdir('evaluate') if f not in [check_sums]]
    files.sort()
    for file in files:
        if file in ignore:
            continue
        s = os.stat(os.path.join('evaluate', file))
        try:
            with open(os.path.join('evaluate', file), 'rb') as f:
                h = crc16(f.read())
                checksum_buffer[file + '_evaluate'] = h
            print('{: <40}  {: >6}  {: >4}'.format(file, h, s[6]))
        except:
            print('{: <40}   ERROR  {: >4}'.format(file, s[6]))

    print('--[TOOLS]--------------------------------------------------')
    files = [f for f in os.listdir('tools') if f not in [check_sums]]
    files.sort()
    for file in files:
        if file in ignore:
            continue
        s = os.stat(os.path.join('tools', file))
        try:
            with open(os.path.join('tools', file), 'rb') as f:
                h = crc16(f.read())
                checksum_buffer[file + '_tools'] = h
            print('{: <40}  {: >6}  {: >4}'.format(file, h, s[6]))
        except:
            print('{: <40}   ERROR  {: >4}'.format(file, s[6]))

    print('--[APPLICATION]--------------------------------------------')
    files = [f for f in os.listdir() if f not in [check_sums]]
    files.sort()
    for file in files:
        if file in ignore:
            continue
        s = os.stat(file)
        try:
            with open(file, 'rb') as f:
                h = crc16(f.read())
                checksum_buffer[file + '_application'] = h
            print('{: <40}  {: >6}  {: >4}'.format(file, h, s[6]))
        except:
            print('{: <40}   ERROR  {: >4}'.format(file, s[6]))

    print('--[CHECKSUM]-----------------------------------------------')
    url = check_sums
    with open(url, 'w') as f:
        f.write(dumps(checksum_buffer))
    try:
        with open(check_sums, 'rb') as f:
            h = crc16(f.read())
            checksum_buffer[check_sums] = h
        print('{: <40}  {: >6}  {: >4}'.format(check_sums, h, s[6]))
    except:
        print('{: <40}   ERROR  {: >4}'.format(check_sums, s[6]))
