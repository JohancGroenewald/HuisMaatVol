from network import WLAN, STA_IF
wifi = WLAN(STA_IF)
# noinspection PyUnresolvedReferences
from ubinascii import hexlify
device_id = hexlify(wifi.config('mac'), ':').decode().upper()

print('device_id: {}'.format(device_id))

from sys import modules
del modules['device_id']
