from os import listdir
# noinspection PyArgumentList
config_module = [f[:-3] for f in listdir() if f.startswith('config_sonoff_')][0]
loaded_module = __import__(config_module)
CONFIG = getattr(loaded_module, 'CONFIG')

# ---------------------------------------------
# Do device setup here to optimize availability
# ---------------------------------------------
leds = CONFIG.get('led', {})
status_led = leds.get(0, {})
from machine import Pin
Pin(status_led['pin'], Pin.OUT).value(status_led['active'])
# ---------------------------------------------
del Pin
del status_led
del leds

from config_local import config
CONFIG.update(config)
CONFIG['config'] = {'file': config_module}
del listdir
del config_module
del loaded_module
del config
