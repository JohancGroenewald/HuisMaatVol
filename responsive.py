# noinspection PyUnresolvedReferences
from wrapper import PinWrapper
import variables as v


def startup(config):
    # ###########################################################################
    # for id, setup in config['button'].items():                                  #
    #     v.button[id] = PinWrapper(
    #         id, config['button'][id]['active'], setup['pin'], PinWrapper.IN
    #     )
    v.button = {
        key: PinWrapper(
            key, config['button'][key]['active'], setup['pin'], PinWrapper.IN
        ) for key, setup in config['button'].values()
    }
    # for id, setup in config['led'].items():
    #     v.led[id] = PinWrapper(
    #         id, config['led'][id]['active'], setup['pin'], PinWrapper.OUT
    #     )
    v.led = {
        key: PinWrapper(
            key, config['led'][key]['active'], setup['pin'], PinWrapper.OUT
        ) for key, setup in config['led'].values()
    }
    # for id, setup in config['relay'].items():
    #     v.relay[id] = PinWrapper(
    #         id, config['relay'][id]['active'], setup['pin'], PinWrapper.OUT
    #     )
    #     v.relays.append(id)                                                     #
    v.relay = {
        key: PinWrapper(
            key, config['relay'][key]['active'], setup['pin'], PinWrapper.OUT
        ) for key, setup in config['relay'].values()
    }
    # ###########################################################################
    for led in v.led.values():                                                  #
        led.off()
    for relay in v.relay.values():
        relay.on()                                                              #
    # ###########################################################################
