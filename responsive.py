# noinspection PyUnresolvedReferences
from machine import Pin
import variables as v


def startup(config):
    v.button = Pin(config['button']['pin'], Pin.IN)
    v.led = Pin(config['led']['pin'], Pin.OUT)
    v.relay = Pin(config['relay']['pin'], Pin.OUT)

    v.led_active = config['led']['active']
    v.led.value(not v.led_active)

    v.relay_active = config['relay']['active']
    v.relay.value(v.relay_active)
