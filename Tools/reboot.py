print('Rebooting in 2 seconds...')
print('Disconnecting WebRepl...')
# noinspection PyUnresolvedReferences
from webrepl import stop
# noinspection PyUnresolvedReferences
from time import sleep_ms
stop()
sleep_ms(500)
stop()
sleep_ms(500)
stop()
sleep_ms(2000)
from machine import reset
reset()
