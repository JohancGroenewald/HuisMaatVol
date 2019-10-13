# noinspection PyUnresolvedReferences
from ubinascii import hexlify
from network import WLAN, STA_IF
_cache = []
_max_label_length = 0


def cache(label, *args):
    global _max_label_length
    if _max_label_length < len(label):
        _max_label_length = len(label)
    _cache.append(
        [label, [arg for arg in args]]
    )


def flush():
    buffer = []
    length = _max_label_length + 1
    max_length = 0
    for (label, args) in _cache:
        len_label = len(label)
        if len_label < length:
            label += ' '*(length - len_label)
        m = '{}: {}'.format(label, args)
        if len(m) > max_length:
            max_length = len(m)
        buffer.append(m)
    m = '--Report'
    if len(m) < max_length:
        m += '-'*(max_length - len(m))
    buffer.insert(0, m)
    m = '-'*max_length
    buffer.append(m)
    print('\n'.join(buffer))


'''
Notes
State 1 
    Device is already connected to the wifi and has an IP address
State 2
    Device has no pre-established wifi connection
State 3
    Device has rebooted
    Should automatically reconnect to previously connected wifi
    - machine.PWRON_RESET
    - machine.HARD_RESET
    - machine.WDT_RESET
    - machine.DEEPSLEEP_RESET
    - machine.SOFT_RESET
'''

RESET_CAUSES_STRINGS = [
    'PWRON_RESET',
    'HARD_RESET',
    'WDT_RESET',
    'DEEPSLEEP_RESET',
    'SOFT_RESET'
]
WIFI_STATE_STRINGS = [
    'STAT_IDLE',
    'STAT_CONNECTING',
    'STAT_WRONG_PASSWORD',
    'STAT_NO_AP_FOUND',
    'STAT_CONNECT_FAIL',
    'STAT_GOT_IP',
]

# Determine the state
from machine import reset_cause
cache('Reset cause', RESET_CAUSES_STRINGS[reset_cause()])

wlan = WLAN()
cache('Wifi active', wlan.active())
cache('Wifi state', WIFI_STATE_STRINGS[wlan.status()])

flush()
from sys import modules
if __name__ in modules:
    del modules[__name__]
