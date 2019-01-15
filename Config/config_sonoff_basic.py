#  Timer 3 is reserved for internal use.
#  Timer 5 controls the servo drive.
#  Timer 6 is used to signaling ADC / DAC read/write.

import references as R

CONFIG = {
    R.KEY_DEVICE: {
        R.KEY_TYPE: 'ESP8266EX'
    },
    R.KEY_BUTTON: {
        0: {R.KEY_HAL: None, R.KEY_PIN: 0, R.KEY_ACTIVE_STATE: 0, 'states': 1, R.KEY_RELAY: [0]},
    },
    R.KEY_LED: {
        0: {R.KEY_HAL: None, R.KEY_PIN: 13, R.KEY_ACTIVE_STATE: 0, R.KEY_RELAY: [0]},
    },
    R.KEY_RELAY: {
        0: {R.KEY_HAL: None, R.KEY_PIN: 12, R.KEY_ACTIVE_STATE: 1},
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
