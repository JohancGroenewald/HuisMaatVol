import machine
import time

print('Rebooting ... please wait until the WebREPL becomes \'Disconnected\'')
time.sleep(2)
machine.reset()
