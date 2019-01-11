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
    ACTION_CONNECT = 'connect'
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
        # --------------------------------------------------------------------------------------------------------------
        self.connect_to = False
        # --------------------------------------------------------------------------------------------------------------
        self.leds = self.config.get('leds', [])
        self.leds_active = self.config.get('leds''_''active', [])
        self.relays = self.config.get('relays', [])
        self.relays_active = self.config.get('relays''_''active', [])
        self.buttons = self.config.get('buttons', [])
        self.buttons_active = self.config.get('buttons''_''active', [])
        self.buttons_state = self.config.get('buttons''_''state', [])
        # --------------------------------------------------------------------------------------------------------------
        if verbose:
            from time import ticks_ms, ticks_diff
            print('#''.Load time: {}'.format(ticks_diff(ticks_ms(), Application.boot_time)))

    def de_initialize_hardware(self):
        for i, hal in enumerate(self.relays):
            hal.value(not self.relays_active[i])
        for i, hal in enumerate(self.leds):
            hal.value(not self.leds_active[i])

    def run(self, watch_dog=const(600)):
        watch_dog = float(watch_dog)
        from time import sleep_ms
        while self.exit_application is False and (watch_dog == -1 or watch_dog):
            if watch_dog:
                watch_dog -= Application.WATCH_DOG_DECAY
            if Application.verbose:
                self.write('#''[{}]{}'.format(int(watch_dog), ' '*5), end='\r')
            # ##########################################################################################################
            if self.connecting_wifi() is False:
                self.received_mqtt()
            if self.exit_application == self.perform_reboot is False:
                if self.leds[0]:
                    self.leds[0].value(not self.leds[0].value())
                for t in range(49):
                    sleep_ms(10)
                    for i, button in enumerate(self.buttons):
                        debounce_down = 2
                        debounce_up = debounce_down + 2
                        if self.buttons_state[i] <= debounce_down and button.value() == self.buttons_active[i]:
                            self.buttons_state[i] += 1
                            if self.buttons_state[i] > debounce_down:
                                print('#''[{}] button down: {}'.format(int(watch_dog), i))
                        elif debounce_down < self.buttons_state[i] <= debounce_up and button.value() != self.buttons_active[i]:
                            self.buttons_state[i] += 1
                            if self.buttons_state[i] > debounce_up:
                                self.buttons_state[i] = 0
                                print('#''[{}] button up  : {}'.format(int(watch_dog), i))

            # ##########################################################################################################
            collect()
        # ---------------------------------------------
        # Perform system shutdown housekeeping
        # ---------------------------------------------
        self.de_initialize_hardware()
        self.publish_relay_state()
        self.publish_mqtt({'device''_status': 'offline'})
        self.disconnect_mqtt()
        # ---------------------------------------------
        if Application.verbose:
            self.write('#''.Application Run Exit')

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
        pre_shared_key = self.config['wifi']['pre_shared_key']
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
        if self.connect_to:
            preferred, pre_shared_key = self.connect_to
            self.connect_to = False
        else:
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
        self.wifi.connect(ssid, pre_shared_key, bssid=bssid)

    def connecting_wifi(self):
        if self.wifi is not None and self.wifi.isconnected() and self.connect_to is False:
            reconnected = self.reconnect_timeout < self.reconnect_delay
            if reconnected or self.mqtt is None:
                self.connect_mqtt()
                self.publish_mqtt({'device''_status': 'online'})
                self.publish_relay_state()
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

    def disconnect_mqtt(self):
        if self.mqtt is None:
            return
        self.mqtt.disconnect()

    def publish_mqtt(self, message: dict):
        if self.mqtt is None or self.wifi is None or self.wifi.isconnected() is False:
            return False
        from json import dumps
        try:
            message.update({
                'device''_id': self.device_id,
                'device''_type': self.config['device']['type'],
                'device''_name': self.config['device']['name'],
                'config''_file': self.config['config']['file'],
                'essid': self.wifi.config('essid'),
                'version': Application.SUPPORTED_VERSION
            })
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
        relay_status = False
        self_status = False
        version = Application.incoming.get(Application.VERSION, None)
        actions = Application.incoming.get(Application.ACTION, None)
        statuses = Application.incoming.get(Application.STATUS, None)
        if version is not None and version < Application.SUPPORTED_VERSION:
            version = False
        if version and actions is not None:
            action = actions.get(Application.ACTION_ON, [])
            if action:
                relay_status = True
                for relay in action:
                    self.relays[relay].value(self.relays_active[relay])
            action = actions.get(Application.ACTION_OFF, [])
            if action:
                relay_status = True
                for relay in action:
                    self.relays[relay].value(not self.relays_active[relay])
            self.connect_to = actions.get(Application.ACTION_CONNECT, False)
            self.perform_reboot = actions.get(Application.ACTION_REBOOT, False)
            self.exit_application = actions.get(Application.ACTION_EXIT, False)
            if self.perform_reboot:
                self.exit_application = True
        if version and statuses is not None:
            if Application.STATUS_RELAY in statuses:
                relay_status = True
            if Application.STATUS_SELF in statuses:
                self_status = True
        if relay_status:
            self.publish_relay_state()
        if self_status:
            self.publish_self_state()
        Application.incoming = None

    def publish_relay_state(self):
        self.publish_mqtt({
            'relays': {
                'on': [i for i, hal in enumerate(self.relays) if hal.value() == self.relays_active[i]],
                'off': [i for i, hal in enumerate(self.relays) if hal.value() != self.relays_active[i]]
            }
        })

    def publish_self_state(self):
        pass

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
