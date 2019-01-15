from sys import implementation

check_sums = 'checksum.json'
if implementation.name == 'micropython':
    def print_header(heading):
        m = '--[{}]'.format(heading.upper())
        print('{}{}'.format(m, '-'*(70-len(m))))

    def print_line(name, size, crc):
        m = '{: <50}{}{: >6}{}{: >6}'.format(name, ' '*4, size, ' '*4, crc)
        print(m)

    def print_line_error(name):
        m = '{: <50}{}ERROR'.format(name, ' '*15)
        print(m)
    print_header('IMPLEMENTATION')
    print('{}'.format(implementation.name))
    from utime import sleep_ms
    from micropython import opt_level
    re_opt_level = opt_level()
    opt_level(3)
    print('opt_level: {}'.format(opt_level()))
    from gc import collect
    from json import loads
    # noinspection PyUnresolvedReferences
    from ucollections import namedtuple
    file_stat = namedtuple('file_stat', (
        'st_mode', 'st_ino', 'st_dev', 'st_nlink', 'st_uid', 'st_gid', 'st_size', 'st_atime', 'st_mtime', 'st_ctime'
    ))
    from crc16 import crc16_stream
    collect()
    import os
    # noinspection PyUnresolvedReferences
    def micropython():
        collect()
        # noinspection PyUnresolvedReferences
        with open(check_sums) as f:
            checksum_buffer = loads(f.read())
        import uos
        listed = []

        # noinspection PyArgumentList
        files = [f for f in os.listdir()]

        header = None
        for (source, file, checksum) in checksum_buffer:
            sleep_ms(1)
            if header != source:
                print_header(source.upper())
                header = source
            if file in files:
                s = file_stat(*uos.stat(file))
                with open(file, 'rb') as f:
                    h = crc16_stream(f)
                print_line(file, checksum if checksum == h else 'FAILED', s.st_size)
                listed.append(file)

        print_header('LOCAL ONLY')
        for file in files:
            sleep_ms(1)
            if file not in listed:
                s = file_stat(*uos.stat(file))
                with open(file, 'rb') as f:
                    h = crc16_stream(f)
                print_line(file, h, s.st_size)

        print_header('*')
        opt_level(re_opt_level)

    micropython()

    from sys import modules
    if __name__ in modules:
        del modules[__name__]
    del modules['crc16']

else:
    # noinspection PyUnresolvedReferences
    from list_files_local import cpython
    cpython(check_sums, implementation.name)
