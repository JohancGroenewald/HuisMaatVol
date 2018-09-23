# noinspection PyUnresolvedReferences
from machine import Pin
import variables as v


def startup(config):
    v.button = Pin(config['button']['pin'], Pin.IN)
    v.led = Pin(config['led']['pin'], Pin.OUT)
    v.relay = Pin(config['relay']['pin'], Pin.OUT)

    v.led.value(not config['led']['active'])
    v.relay.value(config['relay']['active'])
