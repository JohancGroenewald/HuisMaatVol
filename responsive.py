# noinspection PyUnresolvedReferences
from machine import Pin
import variables as v


def startup(config):
    # ###############################################
    for id, setup in config['button'].items():      #
        v.button[id] = Pin(setup['pin'], Pin.IN)
        v.button_start.append(None)
    for id, setup in config['led'].items():
        v.led[id] = Pin(setup['pin'], Pin.OUT)
    for id, setup in config['relay'].items():
        v.relay[id] = Pin(setup['pin'], Pin.OUT)    #
    # ###############################################
    for id, led in v.led.items():                   #
        led.value(not config['led'][id]['active'])
    for id, relay in v.relay.items():
        relay.value(config['relay'][id]['active'])  #
    # ###############################################
