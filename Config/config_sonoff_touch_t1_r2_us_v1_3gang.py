#  Timer 3 is reserved for internal use.
#  Timer 5 controls the servo drive.
#  Timer 6 is used to signaling ADC / DAC read/write.

import references as R

CONFIG = {
    R.KEY_DEVICE: {
        R.KEY_TYPE: 'ESP8285'
    },
    R.KEY_BUTTON: {
        0: {R.KEY_HAL: None, R.KEY_PIN: 0, R.KEY_ACTIVE_STATE: 0, 'states': 1, R.KEY_RELAY: [0]},
        1: {R.KEY_HAL: None, R.KEY_PIN: 10, R.KEY_ACTIVE_STATE: 0, 'states': 1, R.KEY_RELAY: [1]},
        2: {R.KEY_HAL: None, R.KEY_PIN: 9, R.KEY_ACTIVE_STATE: 0, 'states': 1, R.KEY_RELAY: [2]},
    },
    R.KEY_LED: {
        0: {R.KEY_HAL: None, R.KEY_PIN: 13, R.KEY_ACTIVE_STATE: 0, R.KEY_RELAY: [0, 1]},
    },
    R.KEY_RELAY: {
        0: {R.KEY_HAL: None, R.KEY_PIN: 12, R.KEY_ACTIVE_STATE: 1},
        1: {R.KEY_HAL: None, R.KEY_PIN: 5, R.KEY_ACTIVE_STATE: 1},
        2: {R.KEY_HAL: None, R.KEY_PIN: 4, R.KEY_ACTIVE_STATE: 1},
    },
    R.KEY_LEDS: [],
    R.KEY_LEDS_ACTIVE: [],
    R.KEY_RELAYS: [],
    R.KEY_RELAYS_ACTIVE: [],
    R.KEY_BUTTONS: [],
    R.KEY_BUTTONS_ACTIVE: [],
    R.KEY_BUTTONS_STATE: [],
    R.KEY_BUTTONS_RELAYS: [],
}
