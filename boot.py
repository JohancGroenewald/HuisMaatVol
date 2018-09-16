# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)

# noinspection PyUnresolvedReferences
import webrepl
from wifi import WiFi

from config import CONFIG

webrepl.start()
WiFi(CONFIG).connect()

import unload
