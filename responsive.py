# noinspection PyUnresolvedReferences
from wrapper import PinWrapper
import variables as v


def startup(config):
    # ###########################################################################
    v.button = {                                                                #
        key: PinWrapper(
            key, config['button'][key]['active'], setup['pin'], PinWrapper.IN
        ) for key, setup in config['button'].items()
    }
    v.led = {
        key: PinWrapper(
            key, config['led'][key]['active'], setup['pin'], PinWrapper.OUT
        ) for key, setup in config['led'].items()
    }
    v.relay = {
        key: PinWrapper(
            key, config['relay'][key]['active'], setup['pin'], PinWrapper.OUT
        ) for key, setup in config['relay'].items()
    }                                                                           #
    # ###########################################################################
    for led in v.led.values():                                                  #
        led.off()
    for relay in v.relay.values():
        relay.on()                                                              #
    # ###########################################################################
