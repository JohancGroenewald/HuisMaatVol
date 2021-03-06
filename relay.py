from micropython import opt_level
print('{} opt_level: {}'.format(__name__, opt_level()))

from machine import Pin


# noinspection PyUnresolvedReferences,PyArgumentList
class Relay:
    STATE_OFF = 0
    STATE_ON = 1

    def __init__(self, pin, on_level, verbose=0):
        self.verbose = verbose
        self._state = None
        self.gpio_pin = pin
        self.on_level = on_level
        self.pin = Pin(self.gpio_pin, Pin.OUT)
        self.off()

    def __repr__(self):
        return '<Relay: On pin {} at {:x}>'.format(self.gpio_pin, id(self))

    def state(self):
        return self._state

    def off(self):
        self.pin.value(not self.on_level)
        self._state = Relay.STATE_OFF

    def on(self, poll=False):
        self.pin.value(self.on_level)
        self._state = Relay.STATE_ON

    def toggle(self, pulse_width=None):
        self.pin.value(not self.pin.value())
        self._state = not self._state

    def close(self):
        self.off()


class MockRelay:
    STATE_OFF = 0

    def __init__(self):
        pass

    def __repr__(self):
        return '<MockRelay at {:x}>'.format(id(self))

    def state(self):
        return self.STATE_OFF

    def off(self, poll=False):
        pass

    def on(self, poll=False):
        pass

    def toggle(self, pulse_width=None):
        pass

    def close(self):
        pass
