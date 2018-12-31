from network import WLAN, STA_IF
# noinspection PyUnresolvedReferences
from ubinascii import hexlify
from time import sleep

wifi = WLAN(STA_IF)                     # create station interface
device_id = hexlify(wifi.config('mac'), ':').decode().upper()
print('MAC ADDRESS {}'.format(device_id))

print('Activating Wifi')
wifi.active(True)

if wifi.isconnected():
    print(':: Wifi connected')
    print(':: essid = {}'.format(wifi.config('essid')))
else:
    print(':: No wifi connection')

wifi.connect('__x3__pointer__', '_Groenewald1')

from time import sleep
watch_dog = 60
while not wifi.isconnected() and watch_dog:
    print('== watch_dog [{}]'.format(watch_dog))
    print('   essid = {}'.format(wifi.config('essid')))
    print('   status = {}'.format(wifi.status()))
    print('   ifconfig = {}'.format(wifi.ifconfig()))
    sleep(1)
    watch_dog -= 1

if wifi.isconnected():
    print(':: Wifi connected')
    print('   essid = {}'.format(wifi.config('essid')))
    print('   status = {}'.format(wifi.status()))
    print('   ifconfig = {}'.format(wifi.ifconfig()))
else:
    print(':: Wifi connecting failed')

from sys import modules
if __name__ in modules:
    del modules[__name__]
