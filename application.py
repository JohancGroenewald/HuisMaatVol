
def run():
    # #######################################################
    from responsive import startup as responsive_startup    #
    from config import SONOFF_BASIC as config_public
    responsive_startup(config_public)                       #
    # #######################################################
    from config_local import config as config_local
    config_public.update(config_local)                      #
    # #######################################################
    from delayed import start_up as delayed_start_up        #
    # #######################################################
    from gc import collect                                  #
    collect()                                               #
    # #######################################################
    delayed_start_up(config_public)                         #
    # #######################################################
    from gc import collect                                  #
    collect()                                               #
    # #######################################################
