# noinspection PyArgumentList,PyUnresolvedReferences,PyStatementEffect
def run():
    # ###########################################################
    from os import listdir                                      #
    config_module = [
        f[:-3] for f in listdir() if f.startswith('config_sonoff_')
    ][0]
    loaded_module = __import__(config_module)
    CONFIG = getattr(loaded_module, 'CONFIG')                   #
    # ###########################################################
    from responsive import startup as responsive_startup        #
    responsive_startup(CONFIG)                                  #
    # ###########################################################
    from gc import collect                                      #
    collect()                                                   #
    # ###########################################################
    # from micropython import opt_level
    # opt_level(0)
    # ###########################################################
    from config_local import config as config_local             #
    CONFIG.update(config_local)                                 #
    # ###########################################################
    from delayed import start_up as delayed_start_up            #
    # ###########################################################
    collect()                                                   #
    # ###########################################################
    delayed_start_up(CONFIG)                                    #
    # ###########################################################
    collect()                                                   #
    # ###########################################################
