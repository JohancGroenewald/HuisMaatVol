# noinspection PyUnresolvedReferences
from time import ticks_ms, ticks_diff, sleep_ms
from machine import Pin, Timer
import variables as v


def interrupt_handlers():
    v.button.irq(handler=button_interrupt_startup, trigger=Pin.IRQ_FALLING)
    v.timer.init(mode=Timer.PERIODIC, period=v.timer_period, callback=timer_interrupt)
    # v.mqtt


def button_interrupt_startup(button):
    toggle_relay()
    button.irq(handler=button_interrupt_rising, trigger=Pin.IRQ_RISING)


def button_interrupt_rising(button):
    v.button_start = ticks_ms()
    button.irq(handler=button_interrupt_falling, trigger=Pin.IRQ_FALLING)


def button_interrupt_falling(button):
    if v.button_start and ticks_diff(ticks_ms(), v.button_start) >= v.button_delay:
        toggle_relay()
    v.button_start = None
    button.irq(handler=button_interrupt_rising, trigger=Pin.IRQ_RISING)


def timer_interrupt(cls):
    v.led.value(v.led_active)
    sleep_ms(v.led_visual_cycle[0])
    v.led.value(not v.led_active)
    if v.relay.value() == v.relay_active:
        sleep_ms(v.led_visual_cycle[1])
        v.led.value(v.led_active)
        sleep_ms(v.led_visual_cycle[2])
        v.led.value(not v.led_active)


def toggle_relay():
    v.relay.value(not v.relay.value())
