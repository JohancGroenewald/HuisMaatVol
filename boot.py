# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)

# noinspection PyUnresolvedReferences
from gc import collect
# collect()
from webrepl import start
# collect()
from wifi import WiFi
# collect()
from config import CONFIG
# collect()
start()
collect()
WiFi(CONFIG).connect()
# collect()
