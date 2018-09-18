from micropython import opt_level
print('{} opt_level: {}'.format(__name__, opt_level()))

from gc import collect
from network import WLAN, STA_IF
# noinspection PyUnresolvedReferences
from ure import search
from utime import time
from time import sleep
collect()


def singleton(cls):
    instance = None

    def getinstance(*args, **kwargs):
        nonlocal instance
        if instance is None:
            instance = cls(*args, **kwargs)
        return instance
    return getinstance


# noinspection PyUnresolvedReferences,PyArgumentList
@singleton
class WiFi:
    RECONNECT_TIMEOUT = 10

    def __init__(self, config, verbose=0):
        self.verbose = verbose
        self.config = config
        self.__connecting = False
        self.connect_start = None
        self.station = WLAN(STA_IF)

    def __repr__(self):
        return '<WiFi: {}, {} at {:x}>'.format(
            self.station.config('essid'), self.station.ifconfig(), id(self)
        )

    def device_id(self):
        import ubinascii
        return ubinascii.hexlify(self.station.config('mac'),':').decode().upper()

    def connecting(self):
        return self.__connecting

    def connected(self):
        return self.station.isconnected()

    def connect(self):
        if self.__connecting:
            if self.station.isconnected():
                self.__connecting = False
                self.connect_start = None
            elif (time() - self.connect_start) > self.RECONNECT_TIMEOUT:
                # self.station.active(False)
                self.__connecting = False
                self.connect_start = time()
                if self.verbose:
                    print('-> ' 'Connect ' 'timeout')
        elif self.station.isconnected() is False:
            if self.connect_start is None or (time() - self.connect_start) > self.RECONNECT_TIMEOUT:
                if self.verbose:
                    if self.connect_start is None:
                        print('-> ' 'Reconnect ' 'timer started')
                    else:
                        print('-> ' 'Reconnect ' 'timeout')
                self.connect_start = time()
            else:
                return False
            self.station.active(True)
            ssid, password = self.scan()
            if self.verbose:
                print('[{}] [{}]'.format(ssid, password))
            if ssid:
                self.station.connect(ssid, password)
                sleep(1)
                self.__connecting = True
            return True
        return False

    def disconnect(self):
        self.station.disconnect()

    def scan(self):
        ssid, password = None, None
        ap_scan = self.station.scan()
        ap_list = []
        for ap in ap_scan:
            for ssid_mask, password in self.config['wifi']:
                mask = '^{}$'.format(ssid_mask)
                if search(mask, ap[0]):
                    ap_list.append((ap[3], ap[0], password))
        ap_list.sort(reverse=True)
        if self.verbose:
            for ap in ap_list:
                print(ap)
        if len(ap_list):
            ssid, password = ap_list[0][1], ap_list[0][2]
        return ssid, password
