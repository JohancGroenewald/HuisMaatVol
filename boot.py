# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)

from micropython import opt_level
opt_level(3)

# noinspection PyUnresolvedReferences
from gc import collect
# collect()
# noinspection PyUnresolvedReferences
from webrepl import start
# collect()
from wifi import WiFi
# collect()
from config import CONFIG
# collect()
start()
collect()
WiFi(CONFIG).connect()
collect()
