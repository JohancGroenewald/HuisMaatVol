# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)

# noinspection PyUnresolvedReferences
import webrepl
# import wifi
from gc import collect
# import sys

# from config import CONFIG

webrepl.start()
# wifi.WiFi(CONFIG).connect()
# del sys.modules['config']
collect()
