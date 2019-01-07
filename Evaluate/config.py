
def setup():
    from os import listdir
    # noinspection PyArgumentList
    configurations = [f[:-3] for f in listdir() if f.startswith('config_')]
    config_sonoff = None
    config_default = None
    for configuration in configurations:
        if config_sonoff is None and configuration.startswith('config_sonoff_'):
            config_sonoff = configuration
        elif config_default is None and configuration.startswith('config_default_'):
            config_default = configuration
    imported_module = __import__(config_sonoff)
    config = getattr(imported_module, 'CONFIG')
    config['config'] = {'file': config_sonoff}
    if config_default:
        imported_module = __import__(config_default)
        defaults = getattr(imported_module, 'DEFAULTS')
        config.update(defaults)
    # -------------------------------------------------------------
    # Do device setup here to optimize availability
    # -------------------------------------------------------------
    from machine import Pin
    for key, device in config.get('led', {}).items():
        default = config.get('led''_defaults', {}).get(key, False)
        default = device['active'] if default else not device['active']
        Pin(device['pin'], Pin.OUT).value(default)
    for key, device in config.get('relay', {}).items():
        default = config.get('relay''_defaults', {}).get(key, False)
        default = device['active'] if default else not device['active']
        Pin(device['pin'], Pin.OUT).value(default)
    # -------------------------------------------------------------
    # del configurations
    # del config_sonoff
    # del config_default
    # del imported_module
    # del defaults

    from config_local import config as local_config
    config.update(local_config)
    # del local_config
    return config


CONFIG = setup()
# del setup
# import gc
# gc.collect()
