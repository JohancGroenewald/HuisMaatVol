"""
Global configurations

The wifi access point name can be specified using regex.
The wifi key in the CONFIG dictionary must be a list of access points.
"""
# -------------------------------------------------------------------------------------------------------------------- #
from micropython import opt_level
print('{} opt_level: {}'.format(__name__, opt_level()))

from config_local import WIFI_DEVELOPMENT, MQTT_DEVELOPMENT

# -------------------------------------------------------------------------------------------------------------------- #
LED_ESP8266 = {
    'pin': 13,
    'on_level': 0
}
BUTTON_ESP8266 = {
    'pin': 0,
    'on_level': 0
}
RELAY_ESP8266 = {
    'pin': 12,
    'on_level': 1
}
# -------------------------------------------------------------------------------------------------------------------- #
CONFIG_ESP8266 = {
    'type': 'Sonoff Basic'
}
CONFIG_ESP8285 = {
    'type': 'Sonoff Touch'
}
# -------------------------------------------------------------------------------------------------------------------- #
PINOUT_ESP8266 = {
    'led': LED_ESP8266,
    'button': BUTTON_ESP8266,
    'relay': RELAY_ESP8266,
    'ultrasound': None,
    'display': None
}
# -------------------------------------------------------------------------------------------------------------------- #
CONFIG = {
    'device': CONFIG_ESP8266,
    'pinout': PINOUT_ESP8266,
    'wifi': [WIFI_DEVELOPMENT],
    'mqtt': MQTT_DEVELOPMENT
}
# -------------------------------------------------------------------------------------------------------------------- #
