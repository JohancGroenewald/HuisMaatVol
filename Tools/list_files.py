from sys import implementation

check_sums = 'checksum.json'
print('--[IMPLEMENTATION]-----------------------------------------')
print('{}'.format(implementation.name))

if implementation.name == 'micropython':
    from machine import idle
    from utime import sleep_ms
    from micropython import opt_level
    re_opt_level = opt_level()
    opt_level(3)
    print('opt_level: {}'.format(opt_level()))
    from gc import collect
    from json import loads
    # noinspection PyUnresolvedReferences
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
        print('--[EVALUATE]-----------------------------------------------')
        tools = [
            'boot.py',
            'main.py',
            'app.py',
            'config.py',
            'classes.py',
            'mqtt.py'
        ]
        # noinspection PyArgumentList
        files = [f for f in os.listdir() if f in tools]
        files.sort()
        listed.extend(files)
        for file in files:
            sleep_ms(1)
            s = uos.stat(file)
            try:
                with open(file, 'rb') as f:
                    h = crc16_stream(f)
                re_h = checksum_buffer[file + '_evaluate']
                print('{: <35}  {: >4}  {: >6} {: >6} {}'.format(
                    file, s[6], h, re_h, 'OK' if h == re_h else 'FAILED'),
                )
            except:
                print('{: <35}   ERROR  {: >4}'.format(file, s[6]))
        print('--[TOOLS]--------------------------------------------------')
        tools = [
            'cat.py',
            'cleanup.py',
            'cleanup_full.py',
            'crc16.py',
            'delete_file.py',
            'device_id.py',
            'list_files.py',
            'list_files_basic.py',
            'list_modules.py',
            'mem_info.py',
            'reboot.py',
            'unload.py',
            'update.py',
            'wifi_scan.py',
            'wifi_restore.py'
        ]
        # noinspection PyArgumentList
        files = [f for f in os.listdir() if f in tools]
        files.sort()
        listed.extend(files)
        for file in files:
            sleep_ms(1)
            s = uos.stat(file)
            try:
                with open(file, 'rb') as f:
                    h = crc16_stream(f)
                re_h = checksum_buffer[file + '_tools']
                print('{: <35}  {: >4}  {: >6} {: >6} {}'.format(
                    file, s[6], h, re_h, 'OK' if h == re_h else 'FAILED'),
                )
            except:
                print('{: <35}   ERROR  {: >4}'.format(file, s[6]))

        print('--[APPLICATION]--------------------------------------------')
        application = [
            'application.py',
            'boot.py',
            'config_default_on.py',
            'config_default_off.py',
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
            sleep_ms(1)
            s = uos.stat(file)
            try:
                with open(file, 'rb') as f:
                    h = crc16_stream(f)
                re_h = checksum_buffer[file + '_application']
                end = '' if len(file) < 35 else '\n'
                print('{: <35}'.format(file), end=end)
                mask = '{: ' + ('>41' if len(file) > 35 else '>6') + '}  {: >6} {: >6} {}'
                print(mask.format(
                    s[6], h, re_h, 'OK' if h == re_h else 'FAILED'),
                )
            except:
                print('{: <35}   ERROR  {: >4}'.format(file, s[6]))

        print('--[UN GROUPED]---------------------------------------------')
        # noinspection PyArgumentList
        files = [f for f in os.listdir() if f not in listed]
        files.sort()
        for file in files:
            sleep_ms(1)
            s = uos.stat(file)
            try:
                with open(file, 'rb') as f:
                    h = crc16_stream(f)
                print('{: <35}  {: >6}  {: >4}'.format(file, h, s[6]))
            except:
                print('{: <35}   ERROR  {: >4}'.format(file, s[6]))
        opt_level(re_opt_level)

    micropython()

    from sys import modules
    if __name__ in modules:
        del modules[__name__]
    del modules['crc16']

else:
    # noinspection PyUnresolvedReferences
    from list_files_local import cpython
    cpython(check_sums)
