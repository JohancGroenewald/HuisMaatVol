from machine import Pin


def startup(config):
    try:
        button = Pin(config['button']['pin'], Pin.IN)
        led = Pin(config['led']['pin'], Pin.OUT)
        relay = Pin(config['relay']['pin'], Pin.OUT)

        led.value(config['led']['active'])
        relay.value(config['relay']['active'])
    except:
        button, led, relay = None, None, None

    return button, led, relay
