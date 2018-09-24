SONOFF_BASIC = {
    'device': {
        'type': 'ESP8266EX'
    },
    'button': {
        0: {'pin': 0, 'active': 0, 'debounce': 800, 'states': 1},
    },
    'led': {
        0: {'pin': 13, 'active': 0, 'timer': 1, 'period': 5000, 'visual_cycle': [25, 50, 25]},
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
        0: {'pin': 10, 'active': 0, 'debounce': 800, 'states': 2},
        1: {'pin': 0, 'active': 0, 'debounce': 800, 'states': 1},
        2: {'pin': 9, 'active': 0, 'debounce': 800, 'states': 1},
    },
    'led': {
        0: {'pin': 13, 'active': 0, 'timer': 1, 'period': 5000, 'visual_cycle': [25, 50, 25]},
    },
    'relay': {
        0: {'pin': 12, 'active': 1},
        1: {'pin': 5, 'active': 1},
    }
}
