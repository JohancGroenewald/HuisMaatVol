# noinspection PyUnresolvedReferences
from time import sleep_ms
import variables as v

from functions import (
    publish_relay_state,
    mqtt_publish_disconnected,
)

while v.led_interrupt_active:
    sleep_ms(25)
v.mqtt_irq.deinit()
v.led_irq.deinit()
for button in v.button.values():
    button.disconnect()
for led in v.led.values():
    led.off()
for relay in v.relay.values():
    relay.off()
publish_relay_state(v.relays)
sleep_ms(600)
mqtt_publish_disconnected()
sleep_ms(600)
v.mqtt.disconnect()
sleep_ms(250)

v.button = None
v.led = None
v.relay = None
v.relays = None
v.wifi = None
v.mqtt = None
v.led_irq = None
v.mqtt_irq = None
v.config = None

if v.update:
    reset = True

if v.reset:
    import reboot

# noinspection PyUnresolvedReferences
import unload
