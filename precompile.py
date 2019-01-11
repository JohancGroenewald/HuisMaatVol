import os
import mpy_cross

SOURCES = {
    'config': [
        'config_default_off.py',
        'config_default_on.py',
        'config_local.py',
        'config_sonoff_4ch_v2.py',
        'config_sonoff_basic.py',
        'config_sonoff_dual_r2.py',
        'config_sonoff_touch_t1_r2_us_v1_2gang.py',
        'config_sonoff_touch_t1_r2_us_v1_3gang.py'
    ],
    'devices': [
        'config_setup_bed_side_light.py',
        'config_setup_development.py',
        'config_setup_under_table.py',
        'config_setup_workbench.py'
    ],
    'evaluate': [
        'app.py',
        'config.py',
        'classes.py',
        'mqtt.py'
    ],
    'tools': []
}

for (source, files) in SOURCES.items():
    for file in files:
        unc = os.path.join(source, file)
        arguments = '{} -o {}'.format(unc, file)
        print('Generating mpy for {} : {}'.format(unc, arguments))
        mpy_cross.run(unc)
