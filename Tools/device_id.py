from network import WLAN, STA_IF
wifi = WLAN(STA_IF)
from ubinascii import hexlify
device_id = hexlify(wifi.config('mac'), ':').decode().upper()

print('device_id: {}'.format(device_id))

import unload
