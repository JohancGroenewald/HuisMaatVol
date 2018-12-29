def wifi_scan():
    from network import WLAN, STA_IF
    # noinspection PyUnresolvedReferences
    from ubinascii import hexlify

    wifi = WLAN(STA_IF)                     # create station interface
    device_id = hexlify(wifi.config('mac'), ':').decode().upper()
    print('MAC ADDRESS {}'.format(device_id))

    if wifi.active():
        print(':: Wifi already active')
    else:
        print(':: Activating Wifi')
        wifi.active(True)

    ap_list = wifi.scan()                   # scan for access points
    ap_list = [
        (RSSI, hexlify(bssid, ':'), ssid, channel) for (ssid, bssid, channel, RSSI, authmode, hidden) in ap_list
    ]
    ap_list.sort(key=lambda stats: stats[0]*-1)
    for ap in ap_list:
        print(ap)

wifi_scan()
from sys import modules
if __name__ in modules:
    del modules[__name__]
