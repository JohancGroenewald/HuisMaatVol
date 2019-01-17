import time
# noinspection PyUnresolvedReferences
boot_time = time.ticks_ms()
from config import CONFIG, config_time
verbose = 1

import gc
if verbose:
    print('1.' 'Config time: {}'.format(time.ticks_diff(config_time, boot_time)))
    print('1.' 'dir(app):', dir())
    print('1.' 'mem_free(app): {}'.format(gc.mem_free()))
del config_time
from sys import modules
for module in modules:
    if verbose:
        print('#(app) {}'.format(module))
    del modules[module]
# noinspection PyUnboundLocalVariable
del module
del modules
gc.collect()
if verbose:
    print('2.' 'Boot time: {}'.format(time.ticks_diff(time.ticks_ms(), boot_time)))
    print('2.' 'dir(app):', dir())
    print('2.' 'mem_free(app): {}'.format(gc.mem_free()))
# noinspection PyUnresolvedReferences
del time
gc.collect()
try:
    from references import KEY_DEVICE, KEY_VERBOSE, KEY_WATCH_DOG
    from classes import Application
    Application.boot_time = boot_time
    application = Application(CONFIG, verbose=CONFIG[KEY_DEVICE][KEY_VERBOSE])
    application.run(watch_dog=CONFIG[KEY_DEVICE][KEY_WATCH_DOG])
    if application.perform_reboot is True:
        import reboot
    del application
    del Application
    del boot_time
    del KEY_DEVICE
    del KEY_VERBOSE
    del KEY_WATCH_DOG
    del CONFIG
except Exception as e:
    print(e)
import gc
from sys import modules
for module in modules:
    if verbose:
        print('#(app) {}'.format(module))
    del modules[module]
# noinspection PyUnboundLocalVariable
del module
del modules
gc.collect()
if verbose:
    print('3.' 'dir(app):', dir())
    print('3.' 'mem_free(app): ', gc.mem_free())
