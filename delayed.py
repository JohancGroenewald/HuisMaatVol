# noinspection PyUnresolvedReferences
from time import ticks_ms, ticks_diff, sleep_ms
from machine import Pin, Timer

import variables as v


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
    v.led_irq = Timer(v.config['led_irq']['timer'])                                                     #
    v.led_irq.init(mode=Timer.PERIODIC, period=v.config['led_irq']['period'], callback=led_interrupt)   #
    # ###################################################################################################
    for button in v.button.values():                                                                    #
        init_button_irq_trigger(button)                                                                 #
    # ###################################################################################################
    v.mqtt_irq = Timer(v.config['mqtt']['timer'])                                                       #
    init_mqtt_irq()                                                                                     #
    # # #################################################################################################


def init_button_irq_trigger(button):
    for id, _button in v.button.items():
        if button is _button:
            v.button_start[id] = None
            if v.config['button'][id]['active'] == 1:
                v.button[id].irq(handler=button_interrupt_triggered, trigger=Pin.IRQ_RISING)
            else:
                v.button[id].irq(handler=button_interrupt_triggered, trigger=Pin.IRQ_FALLING)
            break


def init_button_irq_debounce(button):
    for id, _button in v.button.items():
        if button is _button:
            v.button_start[id] = ticks_ms
            if v.config['button'][id]['active'] == 1:
                v.button[id].irq(handler=button_interrupt_debounce, trigger=Pin.IRQ_FALLING)
            else:
                v.button[id].irq(handler=button_interrupt_debounce, trigger=Pin.IRQ_RISING)
            break


def button_interrupt_triggered(button):
    init_button_irq_debounce(button)


def button_interrupt_debounce(button):
    for id, _button in v.button.items():
        if button is _button:
            if v.button_start[id] and ticks_diff(ticks_ms(), v.button_start[id]) >= v.config['button'][id]['debounce']:
                toggle_relay(v.config['button'][id]['relay'])
            break
    init_button_irq_trigger(button)


def toggle_relay(relays):
    for relay in relays:
        v.relay[relay].value(not v.relay[relay].value())
    from micropython import schedule
    schedule(publish_relay_state, relays)


def led_interrupt(timer):
    from micropython import schedule
    schedule(led_relay_status, None)


def led_relay_status(argument=None):
    for id, led in v.led.items():
        if v.config['led'][id]['relay'] is None:
            continue
        led.value(v.config['led'][id]['active'])
    sleep_ms(v.config['led_irq']['visual_cycle'][0])
    for id, led in v.led.items():
        if v.config['led'][id]['relay'] is None:
            continue
        led.value(not led.value())
    sleep_ms(v.config['led_irq']['visual_cycle'][1])
    for id, led in v.led.items():
        if v.config['led'][id]['relay'] is None:
            continue
        for relay in v.config['led'][id]['relay']:
            if v.relay[relay].value() == v.config['relay'][relay]['active']:
                led.value(not led.value())
                continue
    sleep_ms(v.config['led_irq']['visual_cycle'][2])
    for id, led in v.led.items():
        if v.config['led'][id]['relay'] is None:
            continue
        led.value(not v.config['led'][id]['active'])


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


def publish_relay_state(relays):
    message = {
        'relay.{}'.format(id): 'on' if v.relay[id].value() == v.config['relay'][id]['active'] else 'off'
        for id in relays
    }
    mqtt_publish(message)


def init_mqtt_irq():
    v.mqtt_irq.init(mode=Timer.PERIODIC, period=v.config['mqtt']['period'], callback=mqtt_interrupt)


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
