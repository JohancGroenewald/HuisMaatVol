from micropython import opt_level
opt_level(2)

# This code will be specific to the ESP8266, ESP8285 and ESP32
# Hopefully I can find a way to identify the type of SOC at boot time.
# This start-up code is for the sake of responsiveness.
try:
    from application import run
    run()
except Exception as e:
    import sys
    # noinspection PyUnresolvedReferences
    sys.print_exception(e)

# noinspection PyUnresolvedReferences
from webrepl import start
start()

from gc import collect
collect()
