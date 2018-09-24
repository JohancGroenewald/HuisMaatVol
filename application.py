
def run():
    # #####################################################
    from responsive import startup as responsive_startup  #
    from config import SONOFF_BASIC as config_public
    responsive_startup(config_public)                     #
    # #####################################################
    from delayed import start_up as delayed_start_up      #
    from config_local import config as config_local
    config_public.update(config_local)
    delayed_start_up(config_public)                       #
    # #####################################################
    from gc import collect
    collect()
