# noinspection PyUnresolvedReferences
from time import ticks_ms, ticks_diff, sleep_ms

import variables as v

from functions import (
    led_interrupt,
    button_triggered,
    init_mqtt_irq
)


# noinspection PyUnresolvedReferences
def start_up(config):
    v.config = config
    # ###################################################################################################
    from network import WLAN, STA_IF                                                                    #
    v.wifi = WLAN(STA_IF)                                                                               #
    # ###################################################################################################
    from ubinascii import hexlify                                                                       #
    v.device_id = hexlify(v.wifi.config('mac'), ':').decode().upper()                                   #
    # ###################################################################################################
    from gc import collect
    collect()
    # ###################################################################################################
    from umqtt_simple import MQTTClient
    v.mqtt = MQTTClient(
        client_id=v.device_id, server=v.config['mqtt']['ip'], port=v.config['mqtt']['port']
    )                                                                                                   #
    # ###################################################################################################
    v.relays.extend([key for key in v.relay.keys()])                                                    #
    # ###################################################################################################
    from machine import Timer                                                                           #
    v.led_irq = Timer(v.config['led_irq']['timer'])
    v.led_irq.init(mode=Timer.PERIODIC, period=v.config['led_irq']['period'], callback=led_interrupt)   #
    # ###################################################################################################
    for button in v.button.values():                                                                    #
        button.trigger(button_triggered)                                                                #
    # ###################################################################################################
    v.mqtt_irq = Timer(v.config['mqtt']['timer'])                                                       #
    init_mqtt_irq()                                                                                     #
    # ###################################################################################################
