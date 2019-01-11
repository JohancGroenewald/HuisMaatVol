#  Timer 3 is reserved for internal use.
#  Timer 5 controls the servo drive.
#  Timer 6 is used to signaling ADC / DAC read/write.

CONFIG = {
    'device': {
        'type': 'ESP8266EX'
    },
    'button': {
        0: {'hal': None, 'pin': 0, 'active': 0, 'debounce': 100, 'states': 1, 'relay': [0]},
    },
    'led': {
        0: {'hal': None, 'pin': 13, 'active': 0, 'relay': [0]},
    },
    'led_irq': {
        'timer': 1, 'period': 5000, 'visual_cycle': [25, 50, 25]
    },
    'relay': {
        0: {'hal': None, 'pin': 12, 'active': 1},
    },
    'leds': [],
    'leds''_''active': [],
    'relays': [],
    'relays''_''active': [],
    'buttons': [],
    'buttons''_''active': [],
    'buttons''_''state': []
}
