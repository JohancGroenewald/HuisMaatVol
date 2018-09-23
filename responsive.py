# noinspection PyUnresolvedReferences
from machine import Pin, Timer
from variables import (
    button, led, relay, timer, mqtt, led_active, relay_active
)


def startup(config):
    global button, led, relay, timer, mqtt
    global led_active, relay_active
    try:
        button = Pin(config['button']['pin'], Pin.IN)
        led = Pin(config['led']['pin'], Pin.OUT)
        relay = Pin(config['relay']['pin'], Pin.OUT)
        timer = Timer(1)
        mqtt = Timer(2)

        led_active = config['led']['active']
        led.value(not led_active)

        relay_active = config['relay']['active']
        relay.value(relay_active)
    except:
        button, led, relay, timer, mqtt = None, None, None, None, None
