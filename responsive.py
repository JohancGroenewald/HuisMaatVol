# noinspection PyUnresolvedReferences
from machine import Pin
import variables as v


def startup(config):
    for id in config['button'].keys():
        setup = config['button'][id]
        v.button[id] = (Pin(setup['pin'], Pin.IN), setup['active'])
    for id in config['led'].keys():
        setup = config['led'][id]
        v.led[id] = (Pin(setup['pin'], Pin.OUT), setup['active'])
    for id in config['relay'].keys():
        setup = config['relay'][id]
        v.relay[id] = (Pin(setup['pin'], Pin.OUT), setup['active'])

    for id, (led, active) in v.led.items():
        led.value(not active)
    for id, (relay, active) in v.relay.items():
        relay.value(active)
