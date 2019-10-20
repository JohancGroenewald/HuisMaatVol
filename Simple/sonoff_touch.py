import machine
import micropython
micropython.alloc_emergency_exception_buf(100)
import ubinascii
import json
from umqtt import simple

BUTTON_1_PIN = 0
BUTTON_2_PIN = 9
RELAY_1_PIN = 12
RELAY_2_PIN = 5

BUTTONS_ACTIVE_STATE = 0
RELAY_ACTIVE_STATE = 1

# MQTT_CLIENT_ID = '0374baf0-f36c-11e9-9c39-cf2c1965569a'
MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id())
MQTT_SERVER='192.168.0.100'
MQTT_ACCESS_TOKEN = 'M0669bB7CT6Q5oP23TNq'
MQTT_PASSWORD = ''
MQTT_TOPIC = 'v1/devices/me/telemetry'


# declare relay callbacks
def handler_for_relay1(event):
    relay1(not relay1())
    telemetry['GANG1'] = relay1()
    micropython.schedule(publish_telemetry, None)


def handler_for_relay2(event):
    relay2(not relay2())
    telemetry['GANG2'] = relay2()
    micropython.schedule(publish_telemetry, None)


def publish_telemetry(args=None):
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


# setup gang interrupts
# Gang 1
gang1 = machine.Pin(BUTTON_1_PIN, machine.Pin.IN)
relay1 = machine.Pin(RELAY_1_PIN, machine.Pin.OUT)
relay1(not RELAY_ACTIVE_STATE)
gang1.irq(handler=handler_for_relay1, trigger=(machine.Pin.IRQ_RISING))

# Gang 2
gang2 = machine.Pin(BUTTON_2_PIN, machine.Pin.IN)
relay2 = machine.Pin(RELAY_2_PIN, machine.Pin.OUT)
relay2(not RELAY_ACTIVE_STATE)
gang2.irq(handler=handler_for_relay2, trigger=(machine.Pin.IRQ_RISING))

telemetry = {'GANG1': relay1(), 'GANG2': relay2()}

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
