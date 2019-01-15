# noinspection PyUnresolvedReferences
from time import ticks_ms, ticks_diff
from gc import collect
from micropython import const
import references as R


class Application:
    RECONNECT_DELAY_MIN = 15.0
    RECONNECT_DELAY_MAX = 60.0
    RECONNECT_GROWTH = 1.0
    RECONNECT_REFRESH = RECONNECT_DELAY_MAX
    TIMEOUT_PIVOT = 0.0
    TIMEOUT_DECAY = 0.5
    WATCH_DOG_DECAY = 0.5
    WATCH_DOG_DEFAULT = const(600)
    WATCH_DOG_DISABLED = const(-1)
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
    STATUS_LED = const(0)
    DEBOUNCE_FLOOR = const(0)
    DEBOUNCE_DOWN = const(40)
    DEBOUNCE_DOWN_LONG = const(500)
    DEBOUNCE_UP = const(40)
    DEBOUNCE_INCREMENT = const(1)
    BUTTON_INACTIVE = const(0)
    BUTTON_UPx1 = const(1)
    BUTTON_UPx2 = const(2)
    SLEEP_CYCLE_DEFAULT = const(270)    # about 500ms
    SLEEP_CYCLE_MARGIN = const(5)
    SLEEP_CYCLE_UPPER_BOUND = const(500+SLEEP_CYCLE_MARGIN)
    SLEEP_CYCLE_LOWER_BOUND = const(500-SLEEP_CYCLE_MARGIN)
    SLEEP_CYCLE_INCREMENT = const(1)
    SLEEP_ONCE = const(1)
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
        self.reconnect_timeout = Application.TIMEOUT_PIVOT
        self.reconnect_refresh = Application.RECONNECT_REFRESH
        self.reconnect_index = 0
        # --------------------------------------------------------------------------------------------------------------
        self.connect_to = False
        # --------------------------------------------------------------------------------------------------------------
        self.leds = self.config.get(R.KEY_LEDS, [])
        self.leds_active = self.config.get(R.KEY_LEDS_ACTIVE, [])
        self.relays = self.config.get(R.KEY_RELAYS, [])
        self.relays_active = self.config.get(R.KEY_RELAYS_ACTIVE, [])
        self.buttons = self.config.get(R.KEY_BUTTONS, [])
        self.buttons_active = self.config.get(R.KEY_BUTTONS_ACTIVE, [])
        self.buttons_state = self.config.get(R.KEY_BUTTONS_STATE, [])
        self.buttons_relays = self.config.get(R.KEY_BUTTONS_RELAYS, [])
        # --------------------------------------------------------------------------------------------------------------
        self.buttons_debounce = [Application.DEBOUNCE_FLOOR]*len(self.buttons)
        self.buttons_pressed = [Application.BUTTON_INACTIVE]*len(self.buttons)
        # --------------------------------------------------------------------------------------------------------------
        if Application.verbose:
            from time import ticks_ms, ticks_diff
            print('#''.Load time: {}'.format(ticks_diff(ticks_ms(), Application.boot_time)))
        # --------------------------------------------------------------------------------------------------------------
        self.loop_profile = 0
        self.sleep_cycle = Application.SLEEP_CYCLE_DEFAULT

    def de_initialize_hardware(self):
        for i, hal in enumerate(self.relays):
            hal.value(not self.relays_active[i])
        for i, hal in enumerate(self.leds):
            hal.value(not self.leds_active[i])

    def run(self, watch_dog=WATCH_DOG_DEFAULT):
        Application.boot_time = ticks_ms()
        watch_dog = float(watch_dog)
        # noinspection PyUnresolvedReferences
        from time import sleep_ms
        button_active, button_down, button_up, button_pressed = None, False, False, False
        while self.exit_application is False and (watch_dog == Application.WATCH_DOG_DISABLED or watch_dog):
            if watch_dog > 0:
                watch_dog -= Application.WATCH_DOG_DECAY
            # ##########################################################################################################
            if Application.verbose:
                self.write(
                    '#''[{: >}:{}ms][SC:{}]{}'.format(
                        int(watch_dog), self.loop_profile, self.sleep_cycle, ' '*15,
                    ),
                    end='\r'
                )
            # ##########################################################################################################
            wifi_connecting = self.connecting_wifi()
            if wifi_connecting is False:
                if self.leds[Application.STATUS_LED]:
                    self.leds[Application.STATUS_LED].value(not self.leds[Application.STATUS_LED].value())
                self.received_mqtt()
            if self.exit_application == self.perform_reboot is False:
                status_led_flash = 50
                for t in range(self.sleep_cycle):
                    sleep_ms(Application.SLEEP_ONCE)
                    if wifi_connecting and status_led_flash == 50:
                        self.leds[Application.STATUS_LED].value(self.leds_active[Application.STATUS_LED])
                        status_led_flash -= 1
                    elif wifi_connecting and status_led_flash == 1:
                        self.leds[Application.STATUS_LED].value(not self.leds_active[Application.STATUS_LED])
                        status_led_flash -= 1
                    elif wifi_connecting and status_led_flash > 0:
                        status_led_flash -= 1
                    for i, button in enumerate(self.buttons):
                        button_active = button.value() == self.buttons_active[i]
                        # ----------------------------------------------------------------------------------------------
                        if button_active and self.buttons_state[i] == Application.BUTTON_INACTIVE:
                            if self.buttons_debounce[i] < Application.DEBOUNCE_DOWN:
                                self.buttons_debounce[i] += Application.DEBOUNCE_INCREMENT
                            else:
                                self.buttons_state[i] = Application.BUTTON_UPx1
                        elif not button_active and self.buttons_state[i] == Application.BUTTON_INACTIVE:
                            if self.buttons_debounce[i] > Application.DEBOUNCE_FLOOR:
                                self.buttons_debounce[i] -= Application.DEBOUNCE_INCREMENT
                        # ----------------------------------------------------------------------------------------------
                        if button_active and self.buttons_state[i] == Application.BUTTON_UPx1:
                            if self.buttons_debounce[i] < Application.DEBOUNCE_DOWN_LONG:
                                self.buttons_debounce[i] += Application.DEBOUNCE_INCREMENT
                            else:
                                self.buttons_state[i] = Application.BUTTON_UPx2
                                self.buttons_debounce[i] = Application.DEBOUNCE_UP
                        elif not button_active and self.buttons_state[i] == Application.BUTTON_UPx1:
                            if self.buttons_debounce[i] > Application.DEBOUNCE_FLOOR:
                                self.buttons_debounce[i] -= Application.DEBOUNCE_INCREMENT
                            else:
                                self.buttons_state[i] = Application.BUTTON_INACTIVE
                                self.buttons_pressed[i] = Application.BUTTON_UPx1
                                button_pressed = True
                        # ----------------------------------------------------------------------------------------------
                        if button_active and self.buttons_state[i] == Application.BUTTON_UPx2:
                            pass
                        elif not button_active and self.buttons_state[i] == Application.BUTTON_UPx2:
                            if self.buttons_debounce[i] > Application.DEBOUNCE_FLOOR:
                                self.buttons_debounce[i] -= Application.DEBOUNCE_INCREMENT
                            else:
                                self.buttons_state[i] = Application.BUTTON_INACTIVE
                                self.buttons_pressed[i] = Application.BUTTON_UPx2
                                button_pressed = True
                        # ----------------------------------------------------------------------------------------------
                    if not button_pressed:
                        continue
                    button_pressed = False
                    for i, pressed in enumerate(self.buttons_pressed):
                        if pressed == Application.BUTTON_UPx1:
                            self.buttons_pressed[i] = Application.BUTTON_INACTIVE
                            for relay in self.buttons_relays[i]:
                                self.relays[relay].value(not self.relays[relay].value())
                            self.publish_relay_state()
                        elif pressed == Application.BUTTON_UPx2:
                            self.buttons_pressed[i] = Application.BUTTON_INACTIVE
                            self.exit_application = True
            # ##########################################################################################################
            collect()
            self.loop_profile = ticks_diff(ticks_ms(), Application.boot_time)
            if self.loop_profile > Application.SLEEP_CYCLE_UPPER_BOUND:
                self.sleep_cycle -= Application.SLEEP_CYCLE_INCREMENT
            elif self.loop_profile < Application.SLEEP_CYCLE_LOWER_BOUND:
                self.sleep_cycle += Application.SLEEP_CYCLE_INCREMENT
            Application.boot_time = ticks_ms()
        # --------------------------------------------------------------------------------------------------------------
        # Perform system shutdown housekeeping
        # --------------------------------------------------------------------------------------------------------------
        self.de_initialize_hardware()
        self.publish_relay_state()
        self.publish_mqtt({R.KEY_DEVICE_STATUS: R.VALUE_STATUS_OFFLINE})
        self.disconnect_mqtt()
        # --------------------------------------------------------------------------------------------------------------
        if Application.verbose:
            self.write('#''.Application Exit Run-Loop')

    @staticmethod
    def write(*args, **kwargs):
        try:
            print(*args, **kwargs)
        except:
            pass

    # noinspection SpellCheckingInspection
    def connect_wifi(self):
        from network import WLAN, STA_IF
        # noinspection PyUnresolvedReferences
        from ubinascii import hexlify
        if self.wifi is None:
            self.wifi = WLAN(STA_IF)
        if not self.wifi.active():
            self.wifi.active(True)
            return
        if self.device_id is None:
            self.device_id = hexlify(self.wifi.config(R.KEY_MAC), ':').decode().upper()
            if Application.verbose:
                self.write('device_id: {}'.format(self.device_id))
        ssid, bssid, selected_ssid = None, None, self.reconnect_index
        pre_shared_key = self.config[R.KEY_WIFI][R.KEY_PRE_SHARED_KEY]
        if self.wifi.isconnected():
            ssid = self.wifi.config(R.KEY_ESSID)
        if Application.verbose:
            if ssid:
                self.write('Connected to: {}, status: {}'.format(ssid, self.wifi.status()))
                if self.reconnect_refresh > Application.TIMEOUT_PIVOT:
                    return
            else:
                self.write('Not Connected, Status: {}'.format(self.wifi.status()))
                if self.wifi.status() > 0:
                    if self.reconnect_refresh <= Application.TIMEOUT_PIVOT:
                        self.wifi.active(False)
                    return
        ssid_mask = '^{}$'.format(self.config[R.KEY_WIFI][R.KEY_MASK])
        ap_list = self.wifi.scan()
        # noinspection PyUnresolvedReferences
        from ure import search
        ap_list = [
            (_RSSI, _bssid, _ssid.decode('utf-8'), _channel)
            for (_ssid, _bssid, _channel, _RSSI, _, _) in ap_list
            if search(ssid_mask, _ssid)
        ]
        RSSI_INDEX = const(0)
        ap_list.sort(key=lambda stats: stats[RSSI_INDEX]*-1)
        if ap_list and selected_ssid >= len(ap_list):
            self.reconnect_index = Application.TOP_SSID
            self.wifi.active(False)
            return
        if Application.verbose:
            for (_RSSI, _bssid, _ssid, _channel) in ap_list:
                self.write(_RSSI, hexlify(_bssid, ':'), _ssid, _channel)
        if self.connect_to:
            preferred, pre_shared_key = self.connect_to
            self.connect_to = False
        else:
            preferred = self.config[R.KEY_DEVICE][R.KEY_PREFERRED_WIFI_AP]
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
            ssid = ap_list[selected_ssid][Application.SSID_INDEX]
            bssid = ap_list[selected_ssid][Application.BSSID_INDEX]
            if Application.verbose:
                self.write('Assign ssid: {}'.format(ssid))
        elif ap_list and ssid != ap_list[Application.TOP_SSID][Application.SSID_INDEX]:
            ssid = ap_list[Application.TOP_SSID][Application.SSID_INDEX]
            bssid = ap_list[Application.TOP_SSID][Application.BSSID_INDEX]
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
        # noinspection PyUnresolvedReferences
        # from time import sleep_ms
        # watch_dog = 5000
        # while not self.wifi.isconnected() and watch_dog:
        #     sleep_ms(1)
        #     watch_dog -= 1

    def connecting_wifi(self):
        if self.wifi is not None and self.wifi.isconnected() and self.wifi.status() == 5 and self.connect_to is False:
            reconnected = self.reconnect_timeout < self.reconnect_delay
            if reconnected or self.mqtt is None:
                self.connect_mqtt()
                self.publish_mqtt({R.KEY_DEVICE_STATUS: R.VALUE_STATUS_ONLINE})
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
                self.reconnect_index += 1
            self.reconnect_timeout = self.reconnect_delay
        else:
            self.reconnect_timeout -= Application.TIMEOUT_DECAY
        return True

    def connect_mqtt(self):
        if self.mqtt is None:
            from mqtt import MQTTClient
            self.mqtt = MQTTClient(
                client_id=self.device_id,
                server=self.config[R.KEY_MQTT][R.KEY_IP],
                port=self.config[R.KEY_MQTT][R.KEY_PORT]
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
                R.KEY_DEVICE_ID: self.device_id,
                R.KEY_DEVICE_TYPE: self.config[R.KEY_DEVICE][R.KEY_TYPE],
                R.KEY_DEVICE_NAME: self.config[R.KEY_DEVICE][R.KEY_NAME],
                R.KEY_CONFIG_FILE: self.config[R.KEY_CONFIG][R.KEY_FILE],
                R.KEY_ESSID: self.wifi.config(R.KEY_ESSID),
                R.KEY_VERSION: Application.SUPPORTED_VERSION
            })
            self.mqtt.publish(self.config[R.KEY_MQTT][R.KEY_TOPIC], dumps(message))
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
            R.KEY_RELAYS: {
                R.KEY_ON: [i for i, hal in enumerate(self.relays) if hal.value() == self.relays_active[i]],
                R.KEY_OFF: [i for i, hal in enumerate(self.relays) if hal.value() != self.relays_active[i]]
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
