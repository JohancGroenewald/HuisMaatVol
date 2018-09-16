"""
Global configurations

The wifi access point name can be specified using regex.
The wifi key in the CONFIG dictionary must be a list of access points.
"""
# -------------------------------------------------------------------------------------------------------------------- #

WIFI_DEVELOPMENT = ('<SSID>', '<password>')

WIFI_PRODUCTION = ('<SSID>', '<password>')

MQTT_DEVELOPMENT = {
    'ip': '<some ip address>',
    'port': 1883,
    'topic': '<some topic>',
    'subscribe': True | False
}
