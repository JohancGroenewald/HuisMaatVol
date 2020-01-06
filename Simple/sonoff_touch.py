import machine
import ubinascii
import json
import time
import network
import micropython
from umqtt import simple

micropython.alloc_emergency_exception_buf(100)
wifi = network.WLAN(network.STA_IF)

VERBOSE = 0

REBOOT_MS_WAIT = 3000
GANG1 = 0
GANG2 = 1

BUTTON_1_PIN = 0
BUTTON_2_PIN = 9
RELAY_1_PIN = 12
RELAY_2_PIN = 5

LED_1_PIN = 13

BUTTONS_ACTIVE_STATE = 0
RELAY_ACTIVE_STATE = 1
LED_ACTIVE_STATE = 0

# MQTT_CLIENT_ID = '0374baf0-f36c-11e9-9c39-cf2c1965569a'
MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id())
MQTT_SERVER='192.168.0.100'
MQTT_ACCESS_TOKEN = 'M0669bB7CT6Q5oP23TNq'
MQTT_PASSWORD = ''
MQTT_TOPIC = 'v1/devices/me/telemetry'


# declare relay callbacks
def relay1_interrupt(event):
    if irq_state[GANG1] == 0:
        irq_state[GANG1] = 1
        irq_measure[GANG1] = time.ticks_ms()
        led1(LED_ACTIVE_STATE)
    elif irq_state[GANG1] == 1:
        irq_state[GANG1] = 2
        irq_measure[GANG1] = time.ticks_diff(time.ticks_ms(), irq_measure[GANG1])
        if irq_measure[GANG1] > REBOOT_MS_WAIT:
            micropython.schedule(gang_1_long_press, None)
        else:
            micropython.schedule(gang_1_short_press, None)


def relay2_interrupt(event):
    if irq_state[GANG2] == 0:
        irq_state[GANG2] = 1
        irq_measure[GANG2] = time.ticks_ms()
        led1(LED_ACTIVE_STATE)
    elif irq_state[GANG2] == 1:
        irq_state[GANG2] = 2
        irq_measure[GANG2] = time.ticks_diff(time.ticks_ms(), irq_measure[GANG2])
        if irq_measure[GANG2] > REBOOT_MS_WAIT:
            micropython.schedule(gang_2_long_press, None)
        else:
            micropython.schedule(gang_2_short_press, None)


def gang_1_long_press(args=None):
    if VERBOSE:
        print('irq_measure[GANG1]: ' + str(irq_measure[GANG1]))
        print('irq_measure[GANG2]: ' + str(irq_measure[GANG2]))
    machine.disable_irq()
    reboot()


def gang_1_short_press(args=None):
    relay1(not relay1())
    telemetry['GANG1'] = relay1()
    publish_telemetry()
    if VERBOSE:
        print('irq_measure[GANG1]: ' + str(irq_measure[GANG1]))
    led1(not LED_ACTIVE_STATE)
    irq_state[GANG1] = 0


def gang_2_long_press(args=None):
    if VERBOSE:
        print('irq_measure[GANG1]: ' + str(irq_measure[GANG1]))
        print('irq_measure[GANG2]: ' + str(irq_measure[GANG2]))
    machine.disable_irq()
    reboot()


def gang_2_short_press(args=None):
    relay2(not relay2())
    telemetry['GANG2'] = relay2()
    publish_telemetry()
    if VERBOSE:
        print('irq_measure[GANG2]: ' + str(irq_measure[GANG2]))
    led1(not LED_ACTIVE_STATE)
    irq_state[GANG2] = 0


def publish_telemetry(args=None):
    if not wifi.active() or not wifi.isconnected():
        return
    try:
        mqtt.connect()
        mqtt.publish(
            MQTT_TOPIC,
            json.dumps(telemetry)
        )
    finally:
        pass
    try:
        mqtt.disconnect()
    finally:
        pass


def reboot(args=None):
    for _ in range(2000//100):
        led1(not led1())
        time.sleep_ms(100)
    machine.reset()


# setup led
led1 = machine.Pin(LED_1_PIN, machine.Pin.OUT)
led1(not LED_ACTIVE_STATE)

# setup gang pins
# Gang 1
gang1 = machine.Pin(BUTTON_1_PIN, machine.Pin.IN)
relay1 = machine.Pin(RELAY_1_PIN, machine.Pin.OUT)
relay1(not RELAY_ACTIVE_STATE)

# Gang 2
gang2 = machine.Pin(BUTTON_2_PIN, machine.Pin.IN)
relay2 = machine.Pin(RELAY_2_PIN, machine.Pin.OUT)
relay2(not RELAY_ACTIVE_STATE)

telemetry = {'GANG1': relay1(), 'GANG2': relay2()}
irq_state = [0, 0]
irq_measure = [0, 0]

for _ in range(16):
    led1(not led1())
    time.sleep_ms(500)
    if wifi.active() and wifi.isconnected():
        break
led1(LED_ACTIVE_STATE)

# setup mqtt client
mqtt = simple.MQTTClient(
    client_id=MQTT_CLIENT_ID,
    server=MQTT_SERVER,
    port=0,
    user=MQTT_ACCESS_TOKEN,
    password=MQTT_PASSWORD,
    keepalive=0
)

publish_telemetry()
led1(not LED_ACTIVE_STATE)

# setup gang interrupts
gang1.irq(handler=relay1_interrupt, trigger=(machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING))
gang2.irq(handler=relay2_interrupt, trigger=(machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING))
