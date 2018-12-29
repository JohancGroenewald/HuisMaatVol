from gc import collect


# noinspection PyUnresolvedReferences
class Application:
    _mqtt_msg = None

    def __init__(self, verbose=0):
        self.verbose = verbose
        self.device_id = None
        self.wifi = None
        # ---------------------------------------------
        # Do device setup here to optimize availability
        # ---------------------------------------------

        # ---------------------------------------------
        from config_local import config
        self.connect_wifi(config)
        from mqtt import MQTTClient
        self.mqtt = MQTTClient(client_id=self.device_id, server=config['mqtt']['ip'], port=config['mqtt']['port'])
        self.mqtt.set_callback(Application.mqtt_callback)
        if self.wifi.isconnected():
            self.connect_mqtt(self.device_id)
        if self.verbose:
            print('self.device_id:', self.device_id)
        collect()

    def run(self, watch_dog=60):
        from time import sleep
        while watch_dog:
            watch_dog -= 1
            if self.verbose:
                print(' run.loop: >>{}<<'.format(watch_dog), end='\r')
            self.mqtt.check_msg()
            sleep(1)
            collect()
        if self.verbose:
            print()

    # noinspection SpellCheckingInspection
    def connect_wifi(self, config):
        from network import WLAN, STA_IF
        from ubinascii import hexlify
        self.wifi = WLAN(STA_IF)
        if self.device_id is None:
            self.device_id = hexlify(self.wifi.config('mac'), ':').decode().upper()
        ssid = None
        if self.wifi.isconnected():
            ssid = self.wifi.config('essid')
        if self.verbose:
            if ssid:
                print('Connected to: {}'.format(ssid))
            else:
                print('Not Connected')
        ssid_mask = '^{}$'.format(config['wifi']['mask'])
        ap_list = self.wifi.scan()
        from ure import search
        ap_list = [
            (_RSSI, hexlify(_bssid, ':'), _ssid, _channel)
            for (_ssid, _bssid, _channel, _RSSI, _, _) in ap_list
            if search(ssid_mask, _ssid)
        ]
        ap_list.sort(key=lambda stats: stats[0]*-1)
        if self.verbose:
            for ap in ap_list:
                print(ap)
        if ap_list and ssid is None:
            ssid = ap_list[0][2]
            if self.verbose:
                print('Assign ssid: {}'.format(ssid))
        elif ap_list and ssid != ap_list[0][2]:
            ssid = ap_list[0][2]
            if self.verbose:
                print('Assign lowest dBm ssid: {}'.format(ssid))
        elif not ap_list and ssid is None:
            if self.verbose:
                print("No ssid's available to assign")
        else:
            self.wifi.connect(ssid, password=config['wifi']['password'])

    def connect_mqtt(self, device_id):
        self.mqtt.connect()
        self.mqtt.subscribe(device_id)
        self.mqtt.publish(topic='remote_switches', msg='DEBUG')
        print('connect_mqtt')

    @staticmethod
    def mqtt_callback(topic, msg):
        from json import loads
        Application._mqtt_msg = loads(msg)
        print(topic)
        print(Application._mqtt_msg)
