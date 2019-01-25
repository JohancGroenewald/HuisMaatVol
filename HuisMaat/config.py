import os
import references as R


# class R:
#     CONFIG_BASE = 'config''_'
#     CONFIG_SONOFF = 'config''_''sonoff'
#     CONFIG_DEFAULT = 'config''_''default'
#     CONFIG_SETUP = 'config''_''setup'
#     CONFIG_LOCAL = 'config''_''local'
#     UNASSIGNED_DEVICE = 'Unassigned Device'
#     CONFIG_DICTIONARY = 'CONFIG'
#     DEFAULTS_DICTIONARY = 'DEFAULTS'
#     SETUP_DICTIONARY = 'SETUP'
#     LOCAL_DICTIONARY = 'LOCAL'
#
#     KEY_ACTIVE_STATE = 'active'
#     KEY_LED = 'led'
#     KEY_LED_DEFAULTS = 'led''_''defaults'
#     KEY_RELAY = 'relay'
#     KEY_RELAY_DEFAULTS = 'relay''_''defaults'
#     KEY_PIN = 'pin'
#     KEY_CONFIG = 'config'
#     KEY_FILE = 'file'
#     KEY_LEDS = 'leds'
#     KEY_LEDS_ACTIVE = 'leds''_''active'
#     KEY_RELAYS = 'relays'
#     KEY_RELAYS_ACTIVE = 'relays''_''active'
#     KEY_BUTTON = 'button'
#     KEY_BUTTONS = 'buttons'
#     KEY_BUTTONS_ACTIVE = 'buttons''_''active'
#     KEY_BUTTONS_STATE = 'buttons''_''state'
#     KEY_BUTTONS_RELAYS = 'buttons''_''relays'
#     KEY_DEVICE = 'device'
#     KEY_NAME = 'name'


# noinspection PyArgumentList
configurations = [
    f[:f.rfind('.')]
    for f in os.listdir()
    if f.startswith(R.CONFIG_BASE)
]
config_sonoff = None
config_default = None
config_setup = None
config_local = None
imported_setup = {}
for configuration in configurations:
    if config_sonoff is None and configuration.startswith(R.CONFIG_SONOFF):
        config_sonoff = configuration
    elif config_default is None and configuration.startswith(R.CONFIG_DEFAULT):
        config_default = configuration
    elif config_setup is None and configuration.startswith(R.CONFIG_SETUP):
        config_setup = configuration
    elif config_local is None and configuration.startswith(R.CONFIG_LOCAL):
        config_local = configuration
imported_module = __import__(config_sonoff)
CONFIG = getattr(imported_module, R.CONFIG_DICTIONARY)
if config_default:
    imported_module = __import__(config_default)
    imported_setup = getattr(imported_module, R.DEFAULTS_DICTIONARY)
# -------------------------------------------------------------
# Do device setup here to optimize availability
# -------------------------------------------------------------
from machine import Pin
for key, device in CONFIG.get(R.KEY_LED, {}).items():
    default = imported_setup.get(R.KEY_LED_DEFAULTS, {}).get(key, False)
    default = device[R.KEY_ACTIVE_STATE] if default else not device[R.KEY_ACTIVE_STATE]
    Pin(device[R.KEY_PIN], Pin.OUT).value(default)
for key, device in CONFIG.get(R.KEY_RELAY, {}).items():
    default = imported_setup.get(R.KEY_RELAY_DEFAULTS, {}).get(key, False)
    default = device[R.KEY_ACTIVE_STATE] if default else not device[R.KEY_ACTIVE_STATE]
    Pin(device[R.KEY_PIN], Pin.OUT).value(default)
# -------------------------------------------------------------
# noinspection PyUnresolvedReferences
from time import ticks_ms
config_time = ticks_ms()
# -------------------------------------------------------------
CONFIG[R.KEY_CONFIG] = {R.KEY_FILE: config_sonoff}
if config_default:
    CONFIG.update(imported_setup)
# -------------------------------------------------------------
for key, device in CONFIG.get(R.KEY_LED, {}).items():
    CONFIG[R.KEY_LEDS].append(Pin(device[R.KEY_PIN], Pin.OUT))
    CONFIG[R.KEY_LEDS_ACTIVE].append(device[R.KEY_ACTIVE_STATE])
for key, device in CONFIG.get(R.KEY_RELAY, {}).items():
    CONFIG[R.KEY_RELAYS].append(Pin(device[R.KEY_PIN], Pin.OUT))
    CONFIG[R.KEY_RELAYS_ACTIVE].append(device[R.KEY_ACTIVE_STATE])
for key, device in CONFIG.get(R.KEY_BUTTON, {}).items():
    CONFIG[R.KEY_BUTTONS].append(Pin(device[R.KEY_PIN], Pin.IN))
    CONFIG[R.KEY_BUTTONS_ACTIVE].append(device[R.KEY_ACTIVE_STATE])
    CONFIG[R.KEY_BUTTONS_STATE].append(0)
    CONFIG[R.KEY_BUTTONS_RELAYS].append(device[R.KEY_RELAY])
# -------------------------------------------------------------
if config_setup:
    imported_module = __import__(config_setup)
    imported_setup = getattr(imported_module, R.SETUP_DICTIONARY)
    CONFIG[R.KEY_DEVICE].update(imported_setup)
else:
    CONFIG[R.KEY_DEVICE][R.KEY_NAME] = R.UNASSIGNED_DEVICE
if config_local:
    imported_module = __import__(config_local)
    imported_setup = getattr(imported_module, R.LOCAL_DICTIONARY)
    CONFIG.update(imported_setup)

# del R
