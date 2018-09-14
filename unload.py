from sys import modules
from gc import collect
from micropython import mem_info


def run():
    print('{}\n{}\n{}'.format('-' * 69, mem_info(), '-' * 69))
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
    print('{}\n{}\n{}'.format('-' * 69, mem_info(), '-' * 69))


run()
