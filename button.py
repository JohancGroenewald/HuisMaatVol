from micropython import opt_level
print('{} opt_level: {}'.format(__name__, opt_level()))

# noinspection PyUnresolvedReferences
from time import ticks_ms, ticks_diff
from machine import Pin


# noinspection PyUnresolvedReferences,PyArgumentList
class Button:
    DEBOUNCE_DELAY = 40
    STATE_OFF = 0
    STATE_UP = 1
    STATE_ON = 2
    STATE_DOWN = 3
    STATE_TOGGLE = 2
    SHORT_PULSE = 100 - (DEBOUNCE_DELAY * 2)
    LONG_PULSE = 1000 - (DEBOUNCE_DELAY * 2)
    NOT_PRESSED = 0
    SHORT_PRESS = 1
    LONG_PRESS = 2

    def __init__(self, pin, on_level, verbose=0):
        self.verbose = verbose
        self.button_pin = pin
        self.on_level = on_level
        self.start = None
        self.pin = Pin(self.button_pin, Pin.IN)
        self.state = self.STATE_OFF
        self._pressed = self.NOT_PRESSED

    def __repr__(self):
        return '<Button: On pin {} at {:x}>'.format(self.button_pin, id(self))

    def poll(self):
        if self._pressed != self.NOT_PRESSED:
            return
        if self.state == self.STATE_OFF:
            if self.pin.value() == self.on_level:
                if self.verbose:
                    print('STATE_OFF -> on_level')
                self._pressed = self.NOT_PRESSED
                self.state = self.STATE_UP
                self.start = ticks_ms()
        elif self.state == self.STATE_UP:
            ticked = ticks_ms()
            if ticks_diff(ticked, self.start) >= self.DEBOUNCE_DELAY:
                if self.pin.value() == self.on_level:
                    if self.verbose:
                        print('STATE_UP -> on_level')
                    self.state = self.STATE_ON
                    self.start = ticks_ms()
                else:
                    if self.verbose:
                        print('STATE_UP -> off_level')
                    self.state = self.STATE_OFF
                    self.start = None
        elif self.state == self.STATE_ON:
            if self.pin.value() != self.on_level:
                if self.verbose:
                    print('STATE_ON -> off_level')
                self.state = self.STATE_DOWN
        elif self.state == self.STATE_DOWN:
            ticked = ticks_ms()
            if ticks_diff(ticked, self.start) >= self.DEBOUNCE_DELAY:
                if self.pin.value() == self.on_level:
                    self.state = self.STATE_ON
                    if self.verbose:
                        print('STATE_DOWN -> on_level')
                else:
                    delta = ticks_diff(ticked, self.start)
                    if self.verbose:
                        print('STATE_DOWN -> off_level: {}'.format(delta))
                    if delta >= self.LONG_PULSE:
                        self._pressed = self.LONG_PRESS
                    elif delta >= self.SHORT_PULSE:
                        self._pressed = self.SHORT_PRESS
                    self.state = self.STATE_OFF
                    self.start = None
                    if self.verbose:
                        print('self._pressed={}'.format(self._pressed))

    def pressed(self):
        return self._pressed

    def clear(self):
        self._pressed = self.NOT_PRESSED

    def close(self):
        self.state = self.STATE_OFF
        self._pressed = self.NOT_PRESSED
        self.start = None


class MockButton:
    def __init__(self):
        pass

    def __repr__(self):
        return '<MockButton: at {:x}>'.format(id(self))

    def poll(self):
        pass

    def pressed(self):
        return Button.NOT_PRESSED

    def clear(self):
        pass

    def close(self):
        pass