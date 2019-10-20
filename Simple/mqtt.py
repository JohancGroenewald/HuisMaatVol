import machine
import ubinascii
import json
from umqtt import simple

ACCESS_TOKEN = 'M0669bB7CT6Q5oP23TNq'

telemetry = {"GANG1": "ON", "GANG2": "OFF"}

# setup mqtt client
mqtt = simple.MQTTClient(
    # client_id='0374baf0-f36c-11e9-9c39-cf2c1965569a',
    client_id=ubinascii.hexlify(machine.unique_id()),
    server='192.168.0.100',
    port=0,
    user=ACCESS_TOKEN,
    password='',
    keepalive=0
)

persistent = mqtt.connect()

try:
    mqtt.publish(
        "v1/devices/me/telemetry",
        json.dumps(telemetry)
    )
except Exception as e:
    print(e)

mqtt.disconnect()
