import os
import mpy_cross

EVALUATE = 'evaluate'
TOOLS = 'tools'
CONFIG = 'config'

for file in [
    'app.py', 'config.py', 'classes.py', 'mqtt.py'
]:
    unc = os.path.join(EVALUATE, file)
    arguments = '{} -o {}'.format(unc, file)
    print('Generating mpy for {} : {}'.format(unc, arguments))
    mpy_cross.run(unc)

for file in [
    'config_default_off.py',
    'config_default_on.py',
    'config_local.py',
    'config_sonoff_4ch_v2.py',
    'config_sonoff_basic.py',
    'config_sonoff_dual_r2.py',
    'config_sonoff_touch_t1_r2_us_v1_2gang.py',
    'config_sonoff_touch_t1_r2_us_v1_3gang.py'
]:
    unc = os.path.join(CONFIG, file)
    arguments = '{} -o {}'.format(unc, file)
    print('Generating mpy for {} : {}'.format(unc, arguments))
    mpy_cross.run(unc)
