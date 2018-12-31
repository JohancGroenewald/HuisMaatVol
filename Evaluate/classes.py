from gc import collect
from config_local import config


# noinspection PyUnresolvedReferences
class Application:
    RECONNECT_DELAY_MIN = 10.0
    RECONNECT_DELAY_MAX = 60.0
    RECONNECT_GROWTH = 1.0
    TIMEOUT_PIVOT = 0.0
    TIMEOUT_DECAY = 0.5
    TOP_SSID, SSID_INDEX = 0, 2
    mqtt_msg = None

    def __init__(self, verbose=0):
        self.verbose = verbose
        self.device_id = None
        self.wifi = None
        self.mqtt = None
        self.reconnect_delay = Application.RECONNECT_DELAY_MIN
        self.reconnect_timeout = Application.TIMEOUT_PIVOT
        # ---------------------------------------------
        # Do device setup here to optimize availability
        # ---------------------------------------------

        # ---------------------------------------------
        collect()

    def run(self, watch_dog=60):
        from time import sleep_ms
        while watch_dog:
            watch_dog -= 1
            if self.verbose:
                self.write('#[{}]'.format(watch_dog), end='\r')
            # ##########################################################################################################
            if self.connecting_wifi() is False:
                self.received_mqtt()
            for t in range(50):
                sleep_ms(10)
            # ##########################################################################################################
            if self.connecting_wifi() is False:
                self.received_mqtt()
            for t in range(49):
                sleep_ms(10)
            # ##########################################################################################################
            collect()
        if self.verbose:
            self.write()

    def write(self, *args, **kwargs):
        try:
            print(*args, **kwargs)
        except:
            pass

    # noinspection SpellCheckingInspection
    def connect_wifi(self):
        from network import WLAN, STA_IF
        from ubinascii import hexlify
        if self.wifi is None:
            self.wifi = WLAN(STA_IF)
        if not self.wifi.active():
            self.wifi.active(True)
        if self.device_id is None:
            self.device_id = hexlify(self.wifi.config('mac'), ':').decode().upper()
            if self.verbose:
                self.write('device_id: {}'.format(self.device_id))
        ssid = None
        if self.wifi.isconnected():
            ssid = self.wifi.config('essid')
        if self.verbose:
            if ssid:
                self.write('Connected to: {}'.format(ssid))
            else:
                self.write('Not Connected')
        ssid_mask = '^{}$'.format(config['wifi']['mask'])
        ap_list = self.wifi.scan()
        from ure import search
        ap_list = [
            (_RSSI, hexlify(_bssid, ':'), _ssid.decode("utf-8"), _channel)
            for (_ssid, _bssid, _channel, _RSSI, _, _) in ap_list
            if search(ssid_mask, _ssid)
        ]
        ap_list.sort(key=lambda stats: stats[0]*-1)
        if self.verbose:
            for ap in ap_list:
                self.write(ap)
        if config['wifi']['preferred'] and config['wifi']['preferred'] in [ssid for (_, _, ssid, _) in ap_list]:
                ssid = config['wifi']['preferred']
                if self.verbose:
                    self.write('Assign preferred ssid: {}'.format(ssid))
        elif ap_list and ssid is None:
            ssid = ap_list[self.TOP_SSID][self.SSID_INDEX]
            if self.verbose:
                self.write('Assign ssid: {}'.format(ssid))
        elif ap_list and ssid != ap_list[self.TOP_SSID][self.SSID_INDEX]:
            ssid = ap_list[self.TOP_SSID][self.SSID_INDEX]
            if self.verbose:
                self.write('Assign lowest dBm ssid: {}'.format(ssid))
        elif not ap_list and ssid is None:
            if self.verbose:
                self.write("No ssid available to assign")
        elif not ap_list and ssid:
            if self.verbose:
                self.write("Connection unchanged")
            return
        else:
            if self.verbose:
                self.write("Force reconnect to dominant AP")
        self.wifi.connect(ssid, config['wifi']['password'])

    def connecting_wifi(self):
        if self.wifi is not None and self.wifi.isconnected() and self.wifi.status() == 5:
            reconnected = self.reconnect_timeout < self.reconnect_delay
            if reconnected or self.mqtt is None:
                self.connect_mqtt()
                self.publish_mqtt({
                    'reconnect' 'ed': reconnected,
                    'reconnect_timeout': self.reconnect_timeout,
                    'reconnect_delay': self.reconnect_delay
                })
            if reconnected:
                self.reconnect_delay = Application.RECONNECT_DELAY_MIN
                self.reconnect_timeout = self.reconnect_delay
                if self.verbose:
                    self.write('Reconnected to Wifi')
            return False
        elif self.reconnect_timeout <= Application.TIMEOUT_PIVOT:
            self.connect_wifi()
            if self.reconnect_delay < Application.RECONNECT_DELAY_MAX:
                self.reconnect_delay += Application.RECONNECT_GROWTH
            self.reconnect_timeout = self.reconnect_delay
        else:
            self.reconnect_timeout -= Application.TIMEOUT_DECAY
        return True

    def connect_mqtt(self):
        if self.mqtt is None:
            from mqtt import MQTTClient
            self.mqtt = MQTTClient(client_id=self.device_id, server=config['mqtt']['ip'], port=config['mqtt']['port'])
            self.mqtt.set_callback(Application.mqtt_callback)
        self.mqtt.connect()
        self.mqtt.subscribe(self.device_id)

    def publish_mqtt(self, message: dict):
        if self.mqtt is None or self.wifi is None or self.wifi.isconnected() is False:
            return False
        message.update({
            'device_id': self.device_id,
            'essid': self.wifi.config('essid')
        })
        from json import dumps
        try:
            self.mqtt.publish(config['mqtt']['topic'], dumps(message))
        except Exception as e:
            if self.verbose:
                self.write('MQTT publish error: {}'.format(e))
        return True

    def received_mqtt(self):
        if self.mqtt is None or self.wifi is None or self.wifi.isconnected() is False:
            return False
        try:
            self.mqtt.check_msg()
        except Exception as e:
            if self.verbose:
                self.write('MQTT receive error: {}'.format(e))
        return True

    @staticmethod
    def mqtt_callback(topic, msg):
        from json import loads
        Application.mqtt_msg = loads(msg)
        self.write(topic)
        self.write(Application.mqtt_msg)
