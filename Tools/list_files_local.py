import os
from json import dumps
# noinspection PyUnresolvedReferences
from crc16 import crc16


def cpython(check_sums, implementation):

    def print_header(heading):
        m = '--[{}]'.format(heading.upper())
        print('{}{}'.format(m, '-'*(70-len(m))))

    def print_line(name, size, crc):
        m = '{: <50}{}{: >6}{}{: >5}'.format(name, ' '*5, size, ' '*4, crc)
        print(m)

    def print_line_error(name):
        m = '{: <50}{}ERROR'.format(name, ' '*15)
        print(m)

    print_header('IMPLEMENTATION')
    print(implementation)

    ignore = [
        '.git', '.gitignore', '.idea', '__pycache__',
        'Argief', 'Config', 'Devices', 'Evaluate', 'Tools', 'precompile.py'
    ]
    sources = ['Config', 'Devices', 'Evaluate', 'Tools']
    checksum_buffer = []
    for source in sources:
        print_header(source)
        files = [f for f in os.listdir(source) if f not in [check_sums]]
        files.sort()
        for file in files:
            if file in ignore:
                continue
            s = os.stat(os.path.join(source, file))
            try:
                with open(os.path.join(source, file), 'rb') as f:
                    h = crc16(f.read())
                    checksum_buffer.append((source, file, h))
                print_line(file, h, s[6])
            except:
                print_line_error(file)
    print_header('CHECKSUM')
    url = check_sums
    with open(url, 'w') as f:
        f.write(dumps(checksum_buffer))
    try:
        s = os.stat(url)
        with open(check_sums, 'rb') as f:
            h = crc16(f.read())
            checksum_buffer.append(('un-sourced', check_sums, h))
        print_line(check_sums, h, s[6])
    except:
        print_line_error(check_sums)
