from os import listdir
# noinspection PyArgumentList
configurations = [
    f[:f.rfind('.')]
    for f in listdir()
    if f.startswith('config''_')
]
config_sonoff = None
config_default = None
config_setup = None
config_local = None
imported_setup = {}
for configuration in configurations:
    if config_sonoff is None and configuration.startswith('config''_''sonoff'):
        config_sonoff = configuration
    elif config_default is None and configuration.startswith('config''_''default'):
        config_default = configuration
    elif config_setup is None and configuration.startswith('config''_''setup'):
        config_setup = configuration
    elif config_local is None and configuration.startswith('config''_local'):
        config_local = configuration
imported_module = __import__(config_sonoff)
CONFIG = getattr(imported_module, 'CONFIG')
if config_default:
    imported_module = __import__(config_default)
    imported_setup = getattr(imported_module, 'DEFAULTS')
# -------------------------------------------------------------
# Do device setup here to optimize availability
# -------------------------------------------------------------
from machine import Pin
for key, device in CONFIG.get('led', {}).items():
    default = imported_setup.get('led''_''defaults', {}).get(key, False)
    default = device['active'] if default else not device['active']
    Pin(device['pin'], Pin.OUT).value(default)
for key, device in CONFIG.get('relay', {}).items():
    default = imported_setup.get('relay''_''defaults', {}).get(key, False)
    default = device['active'] if default else not device['active']
    Pin(device['pin'], Pin.OUT).value(default)
# -------------------------------------------------------------
# noinspection PyUnresolvedReferences
from time import ticks_ms
config_time = ticks_ms()
# -------------------------------------------------------------
CONFIG['config'] = {'file': config_sonoff}
if config_default:
    CONFIG.update(imported_setup)
# -------------------------------------------------------------
for key, device in CONFIG.get('led', {}).items():
    CONFIG['leds'].append(Pin(device['pin'], Pin.OUT))
    CONFIG['leds''_''active'].append(device['active'])
for key, device in CONFIG.get('relay', {}).items():
    CONFIG['relays'].append(Pin(device['pin'], Pin.OUT))
    CONFIG['relays''_''active'].append(device['active'])
for key, device in CONFIG.get('button', {}).items():
    CONFIG['buttons'].append(Pin(device['pin'], Pin.IN))
    CONFIG['buttons''_''active'].append(device['active'])
    CONFIG['buttons''_''state'].append(0)
# -------------------------------------------------------------
if config_setup:
    imported_module = __import__(config_setup)
    imported_setup = getattr(imported_module, 'SETUP')
    CONFIG['device'].update(imported_setup)
else:
    CONFIG['device']['name'] = 'Unassigned Device'
if config_local:
    imported_module = __import__(config_local)
    imported_setup = getattr(imported_module, 'config')
    CONFIG.update(imported_setup)
