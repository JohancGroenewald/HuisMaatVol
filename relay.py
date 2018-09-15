from micropython import opt_level
print('{} opt_level: {}'.format(__name__, opt_level()))

from machine import Pin


# noinspection PyUnresolvedReferences,PyArgumentList
class Relay:
    STATE_OFF = 0
    STATE_ON = 1

    def __init__(self, pin, on_level, verbose=0):
        self.verbose = verbose
        self.state = None
        self.gpio_pin = pin
        self.on_level = on_level
        self.pin = Pin(self.gpio_pin, Pin.OUT)
        self.off()

    def __repr__(self):
        return '<Relay: On pin {} at {:x}>'.format(self.gpio_pin, id(self))

    def off(self):
        self.relay.value(not self.on_level)
        self.state = Relay.STATE_OFF

    def on(self, poll=False):
        self.relay.value(self.on_level)
        self.state = Relay.STATE_ON

    def toggle(self, pulse_width=None):
        self.relay.value(not self.relay.value())
        self.state = not self.state

    def close(self):
        self.off()


class MockRelay:
    def __init__(self):
        pass

    def __repr__(self):
        return '<MockRelay at {:x}>'.format(id(self))

    def off(self, poll=False):
        pass

    def on(self, poll=False):
        pass

    def toggle(self, pulse_width=None):
        pass

    def close(self):
        pass
