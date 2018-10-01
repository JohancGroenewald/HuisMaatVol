from network import WLAN, STA_IF
wifi = WLAN(STA_IF)
# noinspection PyUnresolvedReferences
from ubinascii import hexlify
device_id = hexlify(wifi.config('mac'), ':').decode().upper()

print('device_id: {}'.format(device_id))
print(wifi.ifconfig())
print('ssid: {}'.format(wifi.config('essid')))

from sys import modules
if __name__ in modules:
    del modules[__name__]
