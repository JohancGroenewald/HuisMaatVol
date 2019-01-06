
def setup():
    from os import listdir
    # noinspection PyArgumentList
    config_module = [f[:-3] for f in listdir() if f.startswith('config_sonoff_')][0]
    loaded_module = __import__(config_module)
    CONFIG = getattr(loaded_module, 'CONFIG')
    CONFIG['config'] = {'file': config_module}
    # -------------------------------------------------------------
    # Do device setup here to optimize availability
    # -------------------------------------------------------------
    from machine import Pin
    devices = CONFIG.get('led', {})
    for device in devices.values():
        Pin(device['pin'], Pin.OUT).value(device['active'])
    devices = CONFIG.get('relay', {})
    for device in devices.values():
        Pin(device['pin'], Pin.OUT).value(device['active'])
    # -------------------------------------------------------------
    # del devices
    # del Pin
    # del listdir
    # del config_module
    # del loaded_module
    from config_local import config
    CONFIG.update(config)
    # del config
    return CONFIG


CONFIG = setup()
del setup
import gc
gc.collect()
