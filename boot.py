from network import WLAN, STA_IF

wifi = WLAN(STA_IF)
wifi.active(True)
wifi.connect('__x6__pointer__', '_Groenewald1')

import webrepl
webrepl.start()
