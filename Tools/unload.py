# noinspection PyUnresolvedReferences
from gc import collect, mem_free

print('mem_free ...', mem_free())

system_modules = [
    # 'flashbdev',
    # 'webrepl',
    # 'webrepl_cfg',
    # 'websocket_helper'
]
message = 'Unloading application module ... '
buffer_len = 0


def print_buffer(module, buffer_len):
    _buffer = '\r{}{}'.format(message, module)
    if len(_buffer) < buffer_len:
        _padding = (' ' * (buffer_len - len(_buffer)))
    else:
        _padding = ''
    print('{}{}'.format(_buffer, _padding), end='')
    return len(_buffer)

from sys import modules
for module in modules:
    buffer_len = print_buffer(module, buffer_len)
    if module not in system_modules:
        del modules[module]

print_buffer('done', buffer_len)

import micropython
print()
print('QStr Info ... ', end='')
micropython.qstr_info()

del micropython

print('Running the GC ... ', end='')
collect()
print('done')
print('mem_free ...', mem_free())
