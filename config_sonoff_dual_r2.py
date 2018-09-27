#  Timer 3 is reserved for internal use.
#  Timer 5 controls the servo drive.
#  Timer 6 is used to signaling ADC / DAC read/write.

CONFIG = {
    'device': {
        'type': 'ESP8285'
    },
    'button': {
        0: {'pin': 10, 'active': 0, 'debounce': 100, 'states': 2, 'relay': [0, 1]},
        1: {'pin': 0, 'active': 0, 'debounce': 100, 'states': 1, 'relay': [0]},
        2: {'pin': 9, 'active': 0, 'debounce': 100, 'states': 1, 'relay': [1]},
    },
    'led': {
        0: {'pin': 13, 'active': 0, 'relay': [0, 1]},
    },
    'led_irq': {
        'timer': 1, 'period': 5000, 'visual_cycle': [25, 50, 25]
    },
    'relay': {
        0: {'pin': 12, 'active': 1},
        1: {'pin': 5, 'active': 1},
    }
}
