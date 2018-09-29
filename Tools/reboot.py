import machine
import time

print('Rebooting ... please wait until the WebREPL becomes \'Disconnected\'')
# noinspection PyUnresolvedReferences
from webrepl import stop
stop()
time.sleep(2)
machine.reset()
