
def run():
    # ###########################################################
    from responsive import startup as responsive_startup        #
    from config_sonoff_dual_r2 import CONFIG
    responsive_startup(CONFIG)                                  #
    # ###########################################################
    from gc import collect                                      #
    collect()                                                   #
    # ###########################################################
    from micropython import opt_level
    opt_level(0)
    # ###########################################################
    from config_local import config as config_local             #
    CONFIG.update(config_local)                                 #
    # ###########################################################
    from delayed import start_up as delayed_start_up            #
    # ###########################################################
    from gc import collect                                      #
    collect()                                                   #
    # ###########################################################
    delayed_start_up(CONFIG)                                    #
    # ###########################################################
    from gc import collect                                      #
    collect()                                                   #
    # ###########################################################
