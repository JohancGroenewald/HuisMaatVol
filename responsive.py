# noinspection PyUnresolvedReferences
from time import ticks_ms, ticks_diff, sleep_ms
from machine import Pin, Timer

button, led, relay, timer = None, None, None, None
button_start = None
button_delay = 800
led_active = None
relay_active = None
timer_period = 3000
led_visual_cycle = [25, 50, 25]


def startup(config):
    global button, led, relay, timer, led_active, relay_active
    try:
        button = Pin(config['button']['pin'], Pin.IN)
        led = Pin(config['led']['pin'], Pin.OUT)
        relay = Pin(config['relay']['pin'], Pin.OUT)
        timer = Timer(1)

        led_active = config['led']['active']
        led.value(not led_active)

        relay_active = config['relay']['active']
        relay.value(relay_active)
    except:
        button, led, relay, timer = None, None, None, None


def interrupt_handlers():
    button.irq(handler=button_interrupt_startup, trigger=Pin.IRQ_FALLING)
    timer.init(mode=Timer.PERIODIC, period=timer_period, callback=timer_interrupt)


def button_interrupt_startup(button):
    toggle_relay()
    button.irq(handler=button_interrupt_rising, trigger=Pin.IRQ_RISING)


def button_interrupt_rising(button):
    global button_start
    button_start = ticks_ms()
    button.irq(handler=button_interrupt_falling, trigger=Pin.IRQ_FALLING)


def button_interrupt_falling(button):
    global button_start
    if button_start and ticks_diff(ticks_ms(), button_start) >= button_delay:
        toggle_relay()
    button_start = None
    button.irq(handler=button_interrupt_rising, trigger=Pin.IRQ_RISING)


def timer_interrupt(cls):
    led.value(led_active)
    sleep_ms(led_visual_cycle[0])
    led.value(not led_active)
    if relay.value() == relay_active:
        sleep_ms(led_visual_cycle[1])
        led.value(led_active)
        sleep_ms(led_visual_cycle[2])
        led.value(not led_active)


def toggle_relay():
    relay.value(not relay.value())
    print('relay in now {}'.format('on' if relay.value() == relay_active else 'off'))
