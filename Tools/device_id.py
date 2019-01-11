from os import listdir

# noinspection PyArgumentList
configurations = [f[:f.rfind('.')] for f in listdir() if f.startswith('config_')]
config_sonoff = None
config_default = None
config_setup = None
imported_setup = None
for configuration in configurations:
    if config_sonoff is None and configuration.startswith('config_sonoff_'):
        config_sonoff = configuration
    elif config_default is None and configuration.startswith('config_default_'):
        config_default = configuration
    elif config_setup is None and configuration.startswith('config_setup_'):
        config_setup = configuration
if config_setup:
    imported_module = __import__(config_setup)
    imported_setup = getattr(imported_module, 'SETUP')
if imported_setup:
    m = 'assignment: {}'.format(imported_setup['name'])
else:
    m = 'assignment: Unassigned Device'
print('-'*len(m))
print(m)
print('-'*len(m))
print('config    : {}'.format(config_sonoff))
from network import WLAN, STA_IF
wifi = WLAN(STA_IF)
# noinspection PyUnresolvedReferences
from ubinascii import hexlify
device_id = hexlify(wifi.config('mac'), ':').decode().upper()

print('device_id : {}'.format(device_id))
print('ssid      : {}'.format(wifi.config('essid')))
print('ip        : {}'.format(wifi.ifconfig()[0]))
print('gateway   : {}'.format(wifi.ifconfig()[1]))
print('dns       : {}'.format(wifi.ifconfig()[3]))

from sys import modules
if __name__ in modules:
    del modules[__name__]
