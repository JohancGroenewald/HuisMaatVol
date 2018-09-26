# noinspection PyUnresolvedReferences
from time import ticks_ms, ticks_diff, sleep_ms

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
    from gc import collect
    collect()
    # ###################################################################################################
    from umqtt_simple import MQTTClient
    v.mqtt = MQTTClient(
        client_id=v.device_id, server=v.config['mqtt']['ip'], port=v.config['mqtt']['port']
    )                                                                                                   #
    # ###################################################################################################
    from machine import Timer
    v.led_irq = Timer(v.config['led_irq']['timer'])                                                     #
    v.led_irq.init(mode=Timer.PERIODIC, period=v.config['led_irq']['period'], callback=led_interrupt)   #
    # ###################################################################################################
    for button in v.button.values():                                                                    #
        button.trigger(button_triggered)                                                                #
    # ###################################################################################################
    v.mqtt_irq = Timer(v.config['mqtt']['timer'])                                                       #
    init_mqtt_irq()                                                                                     #
    # ###################################################################################################


def button_triggered(pin):
    gpio = int(str(pin)[4:-1])
    for button in v.button.values():
        if button.gpio == gpio:
            button.debounce(
                v.config['button'][button.key]['debounce'],
                button_0_debounced if button.key == 0 else
                button_1_debounced if button.key == 1 else
                button_2_debounced if button.key == 2 else
                button_3_debounced
            )
            break


def button_0_debounced(timer):
    button_pressed(0)


def button_1_debounced(timer):
    button_pressed(1)


def button_2_debounced(timer):
    button_pressed(2)


def button_3_debounced(timer):
    button_pressed(3)


def button_pressed(key):
    if v.button[key].state():
        toggle_relay(v.config['button'][key]['relay'])
    v.button[key].trigger(button_triggered)


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
        led.on()
    sleep_ms(v.config['led_irq']['visual_cycle'][0])
    for id, led in v.led.items():
        if v.config['led'][id]['relay'] is None:
            continue
        led.off()
    sleep_ms(v.config['led_irq']['visual_cycle'][1])
    for id, led in v.led.items():
        if v.config['led'][id]['relay'] is None:
            continue
        for relay in v.config['led'][id]['relay']:
            if v.relay[relay].state():
                led.on()
                break
    sleep_ms(v.config['led_irq']['visual_cycle'][2])
    for id, led in v.led.items():
        if v.config['led'][id]['relay'] is None:
            continue
        led.off()


def mqtt_interrupt(timer):
    if v.wifi.isconnected() is False:
        pass
    elif v.wifi.isconnected() is True and not v.mqtt.connected():
        v.mqtt_irq.deinit()
        from micropython import schedule
        schedule(mqtt_connect, None)
    elif v.wifi.isconnected() is True and v.mqtt.connected():
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
    from machine import Timer
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
    v.mqtt.connect()
    mqtt_publish({'state': 'connected'})
    if v.config['mqtt']['subscribe']:
        v.mqtt.set_callback(mqtt_callback)
        v.mqtt.subscribe(v.device_id)
    publish_relay_state(v.relays)
    init_mqtt_irq()


def mqtt_callback(topic, msg):
    from json import loads
    v.incoming = loads(msg)


def perform_actions():
    print(v.incoming)
    if 'action' in v.incoming:
        if 'on' in v.incoming['action']:
            for key in v.incoming['action']['on']:
                v.relay[key].on()
        if 'off' in v.incoming['action']:
            for key in v.incoming['action']['off']:
                v.relay[key].off()
        elif v.incoming['action'] == 'exit':
            perform_shutdown()
            return False
        publish_relay_state(v.relays)
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
