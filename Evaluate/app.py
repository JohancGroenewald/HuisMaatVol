
def main():
    # noinspection PyUnresolvedReferences
    # from time import ticks_ms
    # boot_time = ticks_ms()
    from config import CONFIG
    # verbose = 0
    from micropython import opt_level
    opt_level(0)
    import gc
    # if verbose:
    #     print('opt_level:', opt_level())
    #     from time import ticks_diff
    #     print('1.' 'Boot time: {}'.format(ticks_diff(ticks_ms(), boot_time)))
    #     print('1.' 'dir(app):', dir())
    #     print('1.' 'mem_free(app): {}'.format(gc.mem_free()))
    from sys import modules
    for module in modules:
        # if verbose:
        #     print('#(app) {}'.format(module))
        del modules[module]
    # noinspection PyUnboundLocalVariable
    del module
    del modules
    gc.collect()
    # if verbose:
    #     from time import ticks_diff
    #     print('2.' 'Boot time: {}'.format(ticks_diff(ticks_ms(), boot_time)))
    #     print('2.' 'dir(app):', dir())
    #     print('2.' 'mem_free(app): {}'.format(gc.mem_free()))
    # del ticks_ms
    # if verbose:
    #     del ticks_diff
    gc.collect()
    del gc
    from classes import Application
    # if verbose:
    #     from time import ticks_ms, ticks_diff
    #     print('3.' 'Boot time: {}'.format(ticks_diff(ticks_ms(), boot_time)))
    # Application.boot_time = boot_time
    application = Application(CONFIG, verbose=1)
    application.run()
    if application.perform_reboot is True:
        import reboot
    # noinspection PyUnresolvedReferences
    import gc
    gc.collect()
    # if verbose:
    #     print('3.' 'dir(app):', dir())
    #     print('3.' 'mem_free(app): ', gc.mem_free())


main()
