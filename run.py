from micropython import opt_level
print('{} opt_level: {}'.format(__name__, opt_level()))

import time
from led import Led, MockLed
from button import Button, MockButton
from wifi import WiFi
from messaging import Messaging


# noinspection PyUnresolvedReferences
class RunLoop:
    SLEEP_MS_DEFAULT = 20

    def __init__(self, config, verbose=0):
        self.verbose = verbose
        # ------------------------------------------------------------------------------------------------------------ #
        self.exit = False
        self.config = config
        # ------------------------------------------------------------------------------------------------------------ #
        self.sleep_ms = self.SLEEP_MS_DEFAULT
        # ------------------------------------------------------------------------------------------------------------ #
        # Initialise required services
        if self.config['pinout']['led'] is None:
            self.led = MockLed()
        else:
            self.led = Led(
                self.config['pinout']['led']['pin'],
                self.config['pinout']['led']['on_level']
            )
        if self.config['pinout']['button'] is None:
            self.button = MockButton()
        else:
            self.button = Button(
                self.config['pinout']['button']['pin'],
                self.config['pinout']['button']['on_level']
            )
        self.wifi = WiFi(self.config, verbose=self.verbose)
        self.device_id = self.wifi.device_id()
        self.messaging = Messaging(self.config, self.device_id)
        # ------------------------------------------------------------------------------------------------------------ #
        # Application ready feedback --------------------------------------------------------------------------------- #
        self.led.on(poll=True)
        time.sleep(2)
        self.led.off(poll=True)
        # ------------------------------------------------------------------------------------------------------------ #
        if self.wifi.connected():
            self.on_wifi_connected()
        # ------------------------------------------------------------------------------------------------------------ #
        if self.verbose:
            print('<{} with id {}>'.format(self.config['device']['name'], self.device_id))
            print(self.led)
            print(self.wifi)
            print(self.messaging)

    def on_wifi_connected(self):
        self.led.toggle(500)
        if not self.messaging.connected():
            self.messaging.connect()

    def run(self):
        if self.verbose:
            print('Run loop started')
        state = 0
        while not self.exit:
            # ======================================================================================================== #
            self.led.poll()
            self.button.poll()
            # -------------------------------------------------------------------------------------------------------- #
            if state == 0 and self.button.pressed() == Button.SHORT_PRESS:
                if self.verbose:
                    print('<Button: SHORT_PRESS 0>')
                self.messaging.publish('<Button: SHORT_PRESS 0>')
                relay.value(relay_on_level)
                state = 1
                self.button.clear()
            elif state == 1 and self.button.pressed() > Button.NOT_PRESSED:
                if self.verbose:
                    print('<Button: SHORT_PRESS 1>')
                self.messaging.publish('<Button: SHORT_PRESS 1>')
                relay.value(not relay_on_level)
                state = 0
                self.button.clear()
            elif state == 0 and self.button.pressed() == Button.LONG_PRESS:
                if self.verbose:
                    print('<Button: LONG_PRESS 0>')
                self.messaging.publish('<Button: LONG_PRESS 0>')
                self.led.off()
                state = 2
                self.button.clear()
            elif state == 2 and self.button.pressed() > Button.NOT_PRESSED:
                if self.verbose:
                    print('<Button: LONG_PRESS 2>')
                self.messaging.publish('<Button: LONG_PRESS 2>')
                self.led.toggle(500)
                state = 0
                self.button.clear()
            # -------------------------------------------------------------------------------------------------------- #
            if self.wifi.connected():
                if self.messaging.poll():
                    self.messaging.completed()
            elif self.wifi.connecting():
                self.led.toggle(250)
            elif not self.wifi.connected():
                self.wifi.connect()
                if self.wifi.connected():
                    self.on_wifi_connected()
            # ======================================================================================================== #
            time.sleep_ms(self.sleep_ms)  # Reduce the tightness of the run loop
            # ======================================================================================================== #
        if self.verbose:
            print('Run loop exited')

    def close(self):
        self.exit = True
        if self.led:
            self.led.close()
        if self.messaging:
            self.messaging.disconnect()
        # if self.wifi:
        #     self.wifi.disconnect()            # Don't do this, you will loose connection to the REPL
        if self.verbose:
            print('Run loop closed')
