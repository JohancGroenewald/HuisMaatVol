# This code will be specific to the ESP8266, ESP8285 and ESP32
# Hopefully I can find a way to identify the type of SOC at boot time.
# This start-up code is for the sake of responsiveness.
try:
    # #####################################################
    from responsive import startup as responsive_startup  #
    from config import config as config_public
    responsive_startup(config_public)                     #
    # #####################################################
    from delayed import start_up as delayed_start_up      #
    from config_local import config as config_local
    config_public.update(config_local)
    delayed_start_up(config_public)                       #
    # #####################################################
    from gc import collect
    collect()
except Exception as e:
    import sys
    # noinspection PyUnresolvedReferences
    sys.print_exception(e)

# noinspection PyUnresolvedReferences
from webrepl import start
start()

from gc import collect
collect()
