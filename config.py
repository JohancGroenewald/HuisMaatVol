SONOFF_BASIC = {
    'device': {
        'type': 'ESP8266EX'
    },
    'button': {
        0: {'pin': 0, 'active': 0, 'debounce': 800, 'states': 1, 'relay': [0]},
    },
    'led': {
        0: {'pin': 13, 'active': 0, 'relay': [0]},
    },
    'led_irq': {
        'timer': 1, 'period': 5000, 'visual_cycle': [25, 50, 25]
    },
    'relay': {
        0: {'pin': 12, 'active': 1},
    }
}
SONOFF_DUAL_R2 = {
    'device': {
        'type': 'ESP8285'
    },
    'button': {
        0: {'pin': 10, 'active': 0, 'debounce': 800, 'states': 2, 'relay': [0, 1]},
        1: {'pin': 0, 'active': 0, 'debounce': 800, 'states': 1, 'relay': [0]},
        2: {'pin': 9, 'active': 0, 'debounce': 800, 'states': 1, 'relay': [1]},
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
SONOFF_4CH_V2 = {
    'device': {
        'type': 'ESP8285'
    },
    'button': {
        0: {'pin': 0, 'active': 0, 'debounce': 800, 'states': 1, 'relay': [0]},
        1: {'pin': 9, 'active': 0, 'debounce': 800, 'states': 1, 'relay': [1]},
        2: {'pin': 10, 'active': 0, 'debounce': 800, 'states': 1, 'relay': [2]},
        3: {'pin': 14, 'active': 0, 'debounce': 800, 'states': 1, 'relay': [3]},
    },
    'led': {
        0: {'pin': 13, 'active': 0, 'relay': None},
        1: {'pin': 13, 'active': 0, 'relay': [0]},
        2: {'pin': 13, 'active': 0, 'relay': [1]},
        3: {'pin': 13, 'active': 0, 'relay': [2]},
        4: {'pin': 13, 'active': 0, 'relay': [3]},
    },
    'led_irq': {
        'timer': 1, 'period': 5000, 'visual_cycle': [25, 50, 25]
    },
    'relay': {
        0: {'pin': 12, 'active': 1},
        1: {'pin': 5, 'active': 1},
        2: {'pin': 4, 'active': 1},
        3: {'pin': 15, 'active': 1},
    }
}
