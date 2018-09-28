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
        if v.config['button'][key]['states'] == 1:
            toggle_relay(v.config['button'][key]['relay'])
        elif v.config['button'][key]['states'] == 2:
            flip_relay(v.config['button'][key]['relay'])
    v.button[key].trigger(button_triggered)


def toggle_relay(relays):
    for relay in relays:
        v.relay[relay].value(not v.relay[relay].value())
    from micropython import schedule
    schedule(publish_relay_state, relays)


def flip_relay(relays):
    flipped = 0
    for key in relays:
        if v.relay[key].state():
            flipped += 1
    if flipped == len(relays):
        for key in relays:
            v.relay[key].off()
    else:
        flipped = True if flipped == 0 else False
        for key in relays:
            if flipped is False and v.relay[key].state():
                v.relay[key].off()
                flipped = True
            elif flipped:
                v.relay[key].on()
                flipped = False
                break
        if flipped is True:
            for key in relays:
                v.relay[key].on()
    from micropython import schedule
    schedule(publish_relay_state, relays)


def led_interrupt(timer):
    from micropython import schedule
    schedule(led_indicator, None)


def led_indicator(argument=None):
    if v.wifi.isconnected() is False or v.mqtt.connected() is False:
        v.led[0].on()
        sleep_ms(1000 if v.wifi.isconnected() is False else 500)
        v.led[0].off()
        return
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
    v.led[0].on()
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
        elif v.incoming['action'] == 'reboot':
            mqtt_publish({'action': 'reboot'})
            perform_shutdown(reset=True)
        publish_relay_state(v.relays)
    v.incoming = None
    v.led[0].off()
    return True


def perform_shutdown(reset=False):
    v.mqtt_irq.deinit()
    v.led_irq.deinit()
    mqtt_publish({'state': 'disconnected'})
    sleep_ms(1000)
    for button in v.button.values():
        button.terminate()
    for led in v.led.values():
        led.off()
    for relay in v.relay.values():
        relay.off()
    v.button = None
    v.led = None
    v.relay = None
    v.relays = None
    v.wifi = None
    v.mqtt = None
    v.led_irq = None
    v.mqtt_irq = None
    v.config = None
    v.incoming = None

    if reset:
        from machine import reset
        reset()

    # noinspection PyUnresolvedReferences
    import unload
