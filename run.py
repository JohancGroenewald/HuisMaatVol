from micropython import opt_level
print('{} opt_level: {}'.format(__name__, opt_level()))

# noinspection PyUnresolvedReferences
from time import sleep, sleep_ms
from wifi import WiFi
from messaging import Messaging


# noinspection PyUnresolvedReferences
class RunLoop:
    SLEEP_MS_DEFAULT = 20
    LED_TOGGLE_DEFAULT = 500

    def __init__(self, config, verbose=0):
        self.verbose = verbose
        # ------------------------------------------------------------------------------------------------------------ #
        self.exit = False
        self.config = config
        # ------------------------------------------------------------------------------------------------------------ #
        self.sleep_ms = self.SLEEP_MS_DEFAULT
        # ------------------------------------------------------------------------------------------------------------ #
        # Initialise required services
        # ------------------------------------------------------------------------------------------------------------ #
        if self.config['pinout']['led'] is None:
            from led import MockLed
            self.led = MockLed()
        else:
            from led import Led
            self.led = Led(
                self.config['pinout']['led']['pin'],
                self.config['pinout']['led']['on_level']
            )
        # ------------------------------------------------------------------------------------------------------------ #
        if self.config['pinout']['button'] is None:
            from button import MockButton
            self.button = MockButton()
        else:
            from button import Button
            self.button = Button(
                self.config['pinout']['button']['pin'],
                self.config['pinout']['button']['on_level']
            )
        # ------------------------------------------------------------------------------------------------------------ #
        if self.config['pinout']['relay'] is None:
            from relay import MockRelay
            self.relay = MockRelay()
        else:
            from relay import Relay
            self.relay = Relay(
                self.config['pinout']['relay']['pin'],
                self.config['pinout']['relay']['on_level']
            )
        # ------------------------------------------------------------------------------------------------------------ #
        self.wifi = WiFi(self.config, verbose=self.verbose)
        self.device_id = self.wifi.device_id()
        self.messaging = Messaging(self.config, self.device_id)
        # ------------------------------------------------------------------------------------------------------------ #
        # Application ready feedback --------------------------------------------------------------------------------- #
        self.led.on(poll=True)
        sleep(2)
        self.led.off(poll=True)
        # ------------------------------------------------------------------------------------------------------------ #
        if self.wifi.connected():
            self.on_wifi_connected()
        # ------------------------------------------------------------------------------------------------------------ #
        if self.verbose:
            print('<{} with id {}>'.format(self.config['device']['type'], self.device_id))
            print(self.led)
            print(self.button)
            print(self.relay)
            print(self.wifi)
            print(self.messaging)

    def on_wifi_connected(self):
        self.led.toggle(self.LED_TOGGLE_DEFAULT)
        if not self.messaging.connected():
            self.messaging.connect()

    def run(self):
        if self.verbose:
            print('Run loop started')
        while not self.exit:
            # ======================================================================================================== #
            self.led.poll()
            self.button.poll()
            # -------------------------------------------------------------------------------------------------------- #
            if self.relay.state() == self.relay.STATE_OFF and self.button.pressed() == self.button.SHORT_PRESS:
                if self.verbose:
                    print('<Button: SHORT_PRESS 0>')
                self.messaging.publish({'state': '<Button: SHORT_PRESS, relay state: on>'})
                self.relay.on()
                self.button.clear()
            elif self.relay.state() == self.relay.STATE_ON and self.button.pressed() > self.button.NOT_PRESSED:
                if self.verbose:
                    print('<Button: SHORT_PRESS 1>')
                self.messaging.publish({'state': '<Button: SHORT_PRESS, relay state: off>'})
                self.relay.off()
                self.button.clear()
            elif self.led.enabled() is True and self.button.pressed() == self.button.LONG_PRESS:
                if self.verbose:
                    print('<Button: LONG_PRESS 0>')
                self.messaging.publish({'state': '<Button: LONG_PRESS, led enabled: off>'})
                self.led.enable(False)
                self.led.off()
                self.button.clear()
            elif self.led.enabled() is False and self.button.pressed() > self.button.NOT_PRESSED:
                if self.verbose:
                    print('<Button: LONG_PRESS 2>')
                self.messaging.publish({'state': '<Button: LONG_PRESS, led enabled: on>'})
                self.led.enable(True)
                self.led.toggle(self.LED_TOGGLE_DEFAULT)
                self.button.clear()
            # -------------------------------------------------------------------------------------------------------- #
            if self.wifi.connected():
                if self.messaging.poll():
                    if 'action' in self.messaging.msg:
                        if self.messaging.msg['action'] == 'on':
                            if self.verbose:
                                print('<Relay: on>')
                            self.relay.on()
                        elif self.messaging.msg['action'] == 'off':
                            if self.verbose:
                                print('<Relay: off>')
                            self.relay.off()
                        elif self.messaging.msg['action'] == 'exit':
                            if self.verbose:
                                print('<Application: exit>')
                            self.exit = True
                    self.messaging.completed()
            elif self.wifi.connecting():
                self.led.toggle(250)
            elif not self.wifi.connected():
                self.wifi.connect()
                if self.wifi.connected():
                    self.on_wifi_connected()
            # ======================================================================================================== #
            sleep_ms(self.sleep_ms)  # Reduce the tightness of the run loop
            # ======================================================================================================== #
        if self.verbose:
            print('Run loop exited')

    def close(self):
        self.exit = True
        if self.led:
            self.led.close()
        if self.button:
            self.button.close()
        if self.relay:
            self.relay.close()
        if self.messaging:
            self.messaging.disconnect()
        # if self.wifi:
        #     self.wifi.disconnect()            # Don't do this, you will loose connection to the REPL
        if self.verbose:
            print('Run loop closed')
