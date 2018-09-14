from micropython import opt_level
print('{} opt_level: {}'.format(__name__, opt_level()))

import time
import led
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
            self.led = led.MockLed()
        else:
            self.led = led.Led(
                self.config['pinout']['led']['pin'],
                self.config['pinout']['led']['on_level']
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
        while not self.exit:
            # ======================================================================================================== #
            self.led.poll()
            # -------------------------------------------------------------------------------------------------------- #
            if self.wifi.connected():
                pass
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
