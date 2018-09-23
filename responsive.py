from machine import Pin
from time import ticks_ms, ticks_diff

button, led, relay = None, None, None
button_start = None
button_delay = 500


def startup(config):
    global button, led, relay
    try:
        button = Pin(config['button']['pin'], Pin.IN)
        led = Pin(config['led']['pin'], Pin.OUT)
        relay = Pin(config['relay']['pin'], Pin.OUT)

        led.value(config['led']['active'])
        relay.value(config['relay']['active'])
    except:
        button, led, relay = None, None, None


def interrupt_handlers():
    button.irq(button_interrupt_rising, Pin.IRQ_RISING)


def button_interrupt_rising(button):
    global button_start
    button_start = ticks_ms()
    button.irq(button_interrupt_falling, Pin.IRQ_FALLING)


def button_interrupt_falling(button):
    global button_start
    if button_start and ticks_diff(ticks_ms(), button_start) >= button_delay:
        led.value(not led.value())
        relay.value(not relay.value())
    button_start = None
    button.irq(button_interrupt_rising, Pin.IRQ_RISING)
