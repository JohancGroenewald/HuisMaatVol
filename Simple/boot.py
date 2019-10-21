from network import WLAN, STA_IF

wifi = WLAN(STA_IF)
if wifi.active() is False:
    wifi.active(True)
    wifi.connect('__x6__pointer__', '_Groenewald1')

import webrepl
webrepl.start()
