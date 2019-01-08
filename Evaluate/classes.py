from gc import collect
from micropython import const


# noinspection PyUnresolvedReferences
class Application:
    RECONNECT_DELAY_MIN = 10.0
    RECONNECT_DELAY_MAX = 60.0
    RECONNECT_GROWTH = 1.0
    TIMEOUT_PIVOT = 0.0
    TIMEOUT_DECAY = 0.5
    WATCH_DOG_DECAY = 0.5
    TOP_SSID, BSSID_INDEX, SSID_INDEX = const(0), const(1), const(2)
    SUPPORTED_VERSION = [const(2), const(0)]
    VERSION = 'version'
    ACTION = 'action'
    ACTION_REBOOT = 'reboot'
    ACTION_ON = 'on'
    ACTION_OFF = 'off'
    ACTION_EXIT = 'exit'
    STATUS = 'status'
    STATUS_RELAY = 'relay'
    STATUS_SELF = 'self'
    incoming = None
    boot_time = None
    verbose = 0

    def __init__(self, config, verbose=const(0)):
        self.config = config
        Application.verbose = verbose
        self.exit_application = False
        self.perform_reboot = False
        self.device_id = None
        self.wifi = None
        self.mqtt = None
        self.reconnect_delay = Application.RECONNECT_DELAY_MIN
        self.reconnect_timeout = Application.TIMEOUT_PIVOT + 2
        self.initialize_hardware()
        if verbose:
            from time import ticks_ms, ticks_diff
            print('#''Boot time: {}'.format(ticks_diff(ticks_ms(), Application.boot_time)))

    def initialize_hardware(self):

        pass

    def de_initialize_hardware(self):
        from machine import Pin
        devices = self.config.get('led', {})
        for device in devices.values():
            Pin(device['pin'], Pin.OUT).value(not device['active'])
        devices = self.config.get('relay', {})
        for device in devices.values():
            Pin(device['pin'], Pin.OUT).value(not device['active'])

    def run(self, watch_dog=const(600)):
        watch_dog = float(watch_dog)
        from time import sleep_ms
        while self.exit_application is False and watch_dog:
            watch_dog -= Application.WATCH_DOG_DECAY
            if Application.verbose:
                self.write('#''[{}]  '.format(int(watch_dog)), end='\r')
            # ##########################################################################################################
            if self.connecting_wifi() is False:
                self.received_mqtt()
            if self.exit_application == self.perform_reboot is False:
                for t in range(49):
                    sleep_ms(10)
            # ##########################################################################################################
            collect()
        # ---------------------------------------------
        # Perform system shutdown housekeeping
        # ---------------------------------------------
        self.de_initialize_hardware()
        # ---------------------------------------------
        if Application.verbose:
            self.write()

    @staticmethod
    def write(*args, **kwargs):
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
            if Application.verbose:
                self.write('device_id: {}'.format(self.device_id))
        ssid, bssid = None, None
        if self.wifi.isconnected():
            ssid = self.wifi.config('essid')
        if Application.verbose:
            if ssid:
                self.write('Connected to: {}'.format(ssid))
            else:
                self.write('Not Connected')
        ssid_mask = '^{}$'.format(self.config['wifi']['mask'])
        ap_list = self.wifi.scan()
        from ure import search
        ap_list = [
            (_RSSI, _bssid, _ssid.decode("utf-8"), _channel)
            for (_ssid, _bssid, _channel, _RSSI, _, _) in ap_list
            if search(ssid_mask, _ssid)
        ]
        ap_list.sort(key=lambda stats: stats[0]*-1)
        if Application.verbose:
            for (_RSSI, _bssid, _ssid, _channel) in ap_list:
                self.write(_RSSI, hexlify(_bssid, ':'), _ssid, _channel)
        preferred = self.config['wifi']['preferred']
        if preferred:
            for (_, _bssid, _ssid, _) in ap_list:
                if _ssid == preferred:
                    bssid = _bssid
            if bssid is None:
                preferred = False
        if preferred:
                ssid = preferred
                if Application.verbose:
                    self.write('Assign preferred ssid: {}, bssid: {}'.format(ssid, hexlify(bssid, ':')))
        elif ap_list and ssid is None:
            ssid = ap_list[self.TOP_SSID][self.SSID_INDEX]
            bssid = ap_list[self.TOP_SSID][self.BSSID_INDEX]
            if Application.verbose:
                self.write('Assign ssid: {}'.format(ssid))
        elif ap_list and ssid != ap_list[self.TOP_SSID][self.SSID_INDEX]:
            ssid = ap_list[self.TOP_SSID][self.SSID_INDEX]
            bssid = ap_list[self.TOP_SSID][self.BSSID_INDEX]
            if Application.verbose:
                self.write('Assign lowest dBm ssid: {}'.format(ssid))
        elif not ap_list and ssid is None:
            if Application.verbose:
                self.write("No ssid available to assign")
            return
        elif not ap_list and ssid:
            if Application.verbose:
                self.write("Connection unchanged")
            return
        else:
            if Application.verbose:
                self.write("Force reconnect to dominant AP")
        self.wifi.connect(ssid, self.config['wifi']['password'], bssid=bssid)

    def connecting_wifi(self):
        if self.wifi is not None and self.wifi.isconnected() and self.wifi.status() == const(5):
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
                if Application.verbose:
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
            self.mqtt = MQTTClient(
                client_id=self.device_id, server=self.config['mqtt']['ip'], port=self.config['mqtt']['port']
            )
            self.mqtt.set_callback(Application.mqtt_callback)
        self.mqtt.connect()
        self.mqtt.subscribe(self.device_id)

    def publish_mqtt(self, message: dict):
        if self.mqtt is None or self.wifi is None or self.wifi.isconnected() is False:
            return False
        message.update({
            'device''_id': self.device_id,
            'device''_type': self.config['device']['type'],
            'config''_file': self.config['config']['file'],
            'essid': self.wifi.config('essid'),
            'version': Application.SUPPORTED_VERSION
        })
        from json import dumps
        try:
            self.mqtt.publish(self.config['mqtt']['topic'], dumps(message))
        except Exception as e:
            if Application.verbose:
                self.write('MQTT ''publish'' error: {}'.format(e))
        return True

    def received_mqtt(self):
        if self.mqtt is None or self.wifi is None or self.wifi.isconnected() is False:
            return False
        try:
            self.mqtt.check_msg()
            if Application.incoming is not None:
                self.perform_actions()
        except Exception as e:
            if Application.verbose:
                self.write('MQTT ''receive'' error: {}'.format(e))
        return True

    def perform_actions(self):
        version = Application.incoming.get(Application.VERSION, None)
        actions = Application.incoming.get(Application.ACTION, None)
        statuses = Application.incoming.get(Application.STATUS, None)
        if version is not None and version < Application.SUPPORTED_VERSION:
            version = False
        if version and actions is not None:
            if Application.ACTION_OFF in actions:
                pass
            if Application.ACTION_ON in actions:
                pass
            self.perform_reboot = actions.get(Application.ACTION_REBOOT, False)
            self.exit_application = actions.get(Application.ACTION_EXIT, False)
            if self.perform_reboot:
                self.exit_application = True
        if version and statuses is not None:
            if Application.STATUS_RELAY in statuses:
                pass
            if Application.STATUS_SELF in statuses:
                pass
        Application.incoming = None

    @staticmethod
    def mqtt_callback(topic, msg):
        from json import loads
        try:
            Application.incoming = loads(msg)
            if Application.verbose:
                Application.write('topic: {}'.format(topic))
                Application.write(Application.incoming)
        except Exception as e:
            if Application.verbose:
                Application.write('MQTT ''message load'' error: {}'.format(e))
