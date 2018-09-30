seconds = 3
print('Rebooting in {} seconds...'.format(seconds))
print('Disconnecting WebRepl...')
# noinspection PyUnresolvedReferences
from webrepl import stop
stop()
# noinspection PyUnresolvedReferences
from time import sleep_ms
sleep_ms(seconds * 1000)
from machine import reset
reset()
