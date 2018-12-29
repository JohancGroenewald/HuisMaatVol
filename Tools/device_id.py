from os import listdir

# noinspection PyArgumentList
config_module = [
    f[:-3] for f in listdir() if f.startswith('config_sonoff_')
][0]
print('config   : {}'.format(config_module))

from network import WLAN, STA_IF
wifi = WLAN(STA_IF)
# noinspection PyUnresolvedReferences
from ubinascii import hexlify
device_id = hexlify(wifi.config('mac'), ':').decode().upper()

print('device_id: {}'.format(device_id))
print('ssid     : {}'.format(wifi.config('essid')))
print('ip       : {}'.format(wifi.ifconfig()[0]))
print('gateway  : {}'.format(wifi.ifconfig()[1]))
print('dns      : {}'.format(wifi.ifconfig()[3]))

from sys import modules
if __name__ in modules:
    del modules[__name__]
