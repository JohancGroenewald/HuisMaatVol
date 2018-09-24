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
    init_button_irq_falling()                                                                         #
    v.led_irq.init(mode=Timer.PERIODIC, period=v.config['led']['period'], callback=led_interrupt)
    init_mqtt_irq()                                                                                   #
    # #################################################################################################


def init_mqtt_irq():
    v.mqtt_irq.init(mode=Timer.PERIODIC, period=v.config['mqtt']['period'], callback=mqtt_interrupt)


def init_button_irq_rising():
    v.button.irq(handler=button_interrupt_rising, trigger=Pin.IRQ_RISING)


def init_button_irq_falling():
    v.button.irq(handler=button_interrupt_startup, trigger=Pin.IRQ_FALLING)


def button_interrupt_startup(button):
    toggle_relay()
    init_button_irq_rising()


def button_interrupt_rising(button):
    v.button_start = ticks_ms()
    init_button_irq_falling()


def button_interrupt_falling(button):
    if v.button_start and ticks_diff(ticks_ms(), v.button_start) >= v.config['button']['debounce']:
        toggle_relay()
    v.button_start = None
    init_button_irq_rising()


def led_interrupt(timer):
    v.led.value(v.config['led']['active'])
    sleep_ms(v.config['led']['visual_cycle'][0])
    v.led.value(not v.config['led']['active'])
    if v.relay.value() == v.config['relay']['active']:
        sleep_ms(v.config['led']['visual_cycle'][1])
        v.led.value(v.config['led']['active'])
        sleep_ms(v.config['led']['visual_cycle'][2])
        v.led.value(not v.config['led']['active'])


def mqtt_interrupt(timer):
    if v.wifi.isconnected() is False:
        pass
    elif v.wifi.isconnected() is True and v.mqtt is None:
        v.mqtt_irq.deinit()
        from micropython import schedule
        schedule(mqtt_connect, None)
    elif v.wifi.isconnected() is True and v.mqtt is not None:
        v.mqtt_irq.deinit()
        from micropython import schedule
        schedule(mqtt_incoming, None)


def toggle_relay():
    v.relay.value(not v.relay.value())
    from micropython import schedule
    schedule(publish_relay_state, None)


def publish_relay_state(argument=None):
    mqtt_publish({'action': 'on' if v.relay.value() == v.config['relay']['active'] else 'off'})


def mqtt_publish(message):
    if v.wifi.isconnected() is False or v.mqtt is None:
        return
    message['device_id'] = v.device_id
    message['device_type'] = v.config['device']['type']
    from json import dumps
    v.mqtt.publish(v.config['mqtt']['topic'], dumps(message))


def mqtt_incoming(argument):
    v.mqtt.check_msg()
    if v.incoming is not None:
        if perform_actions() is False:
            return
    init_mqtt_irq()


def mqtt_connect(argument):
    from umqtt_simple import MQTTClient
    v.mqtt = MQTTClient(
        client_id=v.device_id,
        server=v.config['mqtt']['ip'],
        port=v.config['mqtt']['port']
    )
    v.mqtt.connect()
    mqtt_publish({'state': 'connected', 'action': 'on'})
    if v.config['mqtt']['subscribe']:
        v.mqtt.set_callback(mqtt_callback)
        v.mqtt.subscribe(v.device_id)
    init_mqtt_irq()


def mqtt_callback(topic, msg):
    from json import loads
    v.incoming = loads(msg)


def perform_actions():
    if 'action' in v.incoming:
        if v.incoming['action'] == 'on':
            v.relay.value(v.config['relay']['active'])
        elif v.incoming['action'] == 'off':
            v.relay.value(not v.config['relay']['active'])
        elif v.incoming['action'] == 'exit':
            perform_shutdown()
            return False
        publish_relay_state()
    v.incoming = None
    return True


def perform_shutdown():
    mqtt_publish({'state': 'disconnected'})
    v.button.irq(handler=None)
    v.mqtt_irq.deinit()
    v.led_irq.deinit()
    v.led.value(not v.config['led']['active'])
    v.relay.value(not v.config['relay']['active'])
    v.led_irq, v.mqtt_irq = None, None
    v.button, v.led, v.relay, v.wifi, v.mqtt = None, None, None, None, None
    # noinspection PyUnresolvedReferences
    import unload
    from gc import collect
    collect()
