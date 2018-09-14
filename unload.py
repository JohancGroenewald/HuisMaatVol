from sys import modules
from gc import collect


def run():
    system_modules = [
        # 'flashbdev',
        # 'webrepl',
        # 'webrepl_cfg',
        # 'websocket_helper'
    ]
    message = 'Unloading application module ... '
    buffer_len = 0

    def print_buffer(module, buffer_len):
        buffer = '\r{}{}'.format(message, module)
        if len(buffer) < buffer_len:
            padding = (' ' * (buffer_len - len(buffer)))
        else:
            padding = ''
        print('{}{}'.format(buffer, padding), end='')
        return len(buffer)

    for module in modules:
        buffer_len = print_buffer(module, buffer_len)
        if module not in system_modules:
            del modules[module]
    print_buffer('done', buffer_len)
    print('\nRunning the GC ... ', end='')
    print('done')
    if 'unload' in modules:
        del modules['unload']

    collect()


run()
