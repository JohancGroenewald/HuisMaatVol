device_id = None

button = {}
led = {}
relay = {}
relays = []

wifi, mqtt = None, None

led_irq, mqtt_irq = None, None

config = None
incoming = None

tmp_id = None
tmp_button = None

led_interrupt_active = False
shutdown = False
reconnected = False

update = False
reset = False
