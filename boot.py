# This code will be specific to the ESP8266, ESP8285 and ESP32
# Hopefully I can find a way to identify the type of SOC at boot time.
# This start-up code is for the sake of responsiveness.
from responsive import startup, interrupt_handlers

config = {
    'device': 'ESP8266',
    'button': {'pin': 0, 'active': 0},
    'led': {'pin': 13, 'active': 0},
    'relay': {'pin': 12, 'active': 1}
}
startup(config)
interrupt_handlers()

# noinspection PyUnresolvedReferences
from webrepl import start
start()

from gc import collect
collect()
