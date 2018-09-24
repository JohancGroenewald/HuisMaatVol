# noinspection PyUnresolvedReferences
from wrapper import PinWrapper
import variables as v


def startup(config):
    # ###################################################################
    for id, setup in config['button'].items():                          #
        v.button[id] = PinWrapper(
            id, config['button'][id]['active'], setup['pin'], PinWrapper.IN
        )
    for id, setup in config['led'].items():
        v.led[id] = PinWrapper(
            id, config['led'][id]['active'], setup['pin'], PinWrapper.OUT
        )
    for id, setup in config['relay'].items():
        v.relay[id] = PinWrapper(
            id, config['relay'][id]['active'], setup['pin'], PinWrapper.OUT
        )                                                               #
    # ###################################################################
    for led in v.led.values():                                          #
        led.off()
    for relay in v.relay.values():
        relay.on()                                                      #
    # ###################################################################
