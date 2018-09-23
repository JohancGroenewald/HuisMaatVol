# noinspection PyUnresolvedReferences
from time import ticks_ms, ticks_diff, sleep_ms
from machine import Pin, Timer

import variables as v


# noinspection PyUnresolvedReferences
def start_up(config):
    v.config = config
    # #################################################################################################
    from network import WLAN, STA_IF                                                                  #
    v.wifi = WLAN(STA_IF)                                                                             #
    # #################################################################################################
    from ubinascii import hexlify                                                                     #
    v.device_id = hexlify(v.wifi.config('mac'),':').decode().upper()                                  #
    # #################################################################################################
    v.led_irq = Timer(v.config['led']['timer'])                                                       #
    v.mqtt_irq = Timer(v.config['mqtt']['timer'])                                                     #
    # #################################################################################################
    v.button.irq(handler=button_interrupt_startup, trigger=Pin.IRQ_FALLING)                           #
    v.led_irq.init(mode=Timer.PERIODIC, period=v.config['led']['period'], callback=led_interrupt)
    v.mqtt_irq.init(mode=Timer.PERIODIC, period=v.config['mqtt']['period'], callback=mqtt_interrupt)  #
    # #################################################################################################


def button_interrupt_startup(button):
    toggle_relay()
    button.irq(handler=button_interrupt_rising, trigger=Pin.IRQ_RISING)


def button_interrupt_rising(button):
    v.button_start = ticks_ms()
    button.irq(handler=button_interrupt_falling, trigger=Pin.IRQ_FALLING)


def button_interrupt_falling(button):
    if v.button_start and ticks_diff(ticks_ms(), v.button_start) >= v.config['button']['debounce']:
        toggle_relay()
    v.button_start = None
    button.irq(handler=button_interrupt_rising, trigger=Pin.IRQ_RISING)


def led_interrupt(timer):
    v.led.value(v.led_active)
    sleep_ms(v.config['led']['visual_cycle'][0])
    v.led.value(not v.led_active)
    if v.relay.value() == v.relay_active:
        sleep_ms(v.config['led']['visual_cycle'][1])
        v.led.value(v.led_active)
        sleep_ms(v.config['led']['visual_cycle'][2])
        v.led.value(not v.led_active)


def mqtt_interrupt(timer):
    if v.wifi.isconnected() is False:
        pass
    elif v.wifi.isconnected() is True and v.mqtt is None:
        from machine import disable_irq, enable_irq
        irq_state = disable_irq()
        from umqtt_simple import MQTTClient
        v.mqtt = MQTTClient(
            client_id=v.device_id,
            server=v.config['mqtt']['ip'],
            port=v.config['mqtt']['port']
        )
        v.mqtt.connect()
        publish({'state': 'connected'})
        # if config['mqtt']['subscribe']:
        #     self.mqtt.set_callback(self.callback)
        #     self.mqtt.subscribe(self.device_id)#
        enable_irq(irq_state)
    elif v.wifi.isconnected() is True and v.mqtt is not None:
        # listen for messages
        pass


def toggle_relay():
    v.relay.value(not v.relay.value())


def publish(message):
    message['device_id'] = v.device_id
    message['device_type'] = v.config['device']['type']
    from json import dumps
    v.mqtt.publish(v.config['mqtt']['topic'], dumps(message))
