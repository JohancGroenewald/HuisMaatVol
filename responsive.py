# noinspection PyUnresolvedReferences
from machine import Pin
import variables as v


def startup(config):
    for id, setup in config['button']:
        v.button[id] = Pin(setup['pin'], Pin.IN)
    for id, setup in config['led']:
        v.led[id] = Pin(setup['pin'], Pin.OUT)
    for id, setup in config['relay']:
        v.relay[id] = Pin(setup['pin'], Pin.OUT)

    for id, led in v.led.items():
        active = config['led'][id]['active']
        led.value(not active)

    for id, relay in v.relay.items():
        active = config['relay'][id]['active']
        relay.value(active)
