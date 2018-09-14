from micropython import opt_level
print('{} opt_level: {}'.format(__name__, opt_level()))

import json
from umqtt_robust import MQTTClient


class Messaging:
    def __init__(self, config, device_id):
        self.config = config
        self.device_id = device_id
        self.mqtt = None

    def __repr__(self):
        return '<Messaging: {}, {}, {}:{}, {} at {:x}>'.format(
            self.device_id,
            'MQTT',
            self.config['mqtt']['ip'],
            self.config['mqtt']['port'],
            self.mqtt,
            id(self)
        )

    def poll(self):
        if self.mqtt is not None:
            self.mqtt.check_msg()

    @staticmethod
    def callback(topic, msg):
        print(topic, msg)

    def connect(self, subscribe=False):
        if self.mqtt is None:
            self.mqtt = MQTTClient(
                client_id=self.device_id, server=self.config['mqtt']['ip'], port=self.config['mqtt']['port']
            )
            self.mqtt.connect()
            message = {'state': 'connected'}
            self.publish(message)
            if subscribe:
                self.mqtt.set_callback(self.callback)
                self.mqtt.subscribe(self.device_id)

    def publish(self, message):
        message['device_id'] = self.device_id
        self.mqtt.publish(self.config['mqtt']['topic'], json.dumps(message))

    def disconnect(self):
        if self.mqtt:
            message = {'state': 'disconnected'}
            self.publish(message)
            self.mqtt.disconnect()
            self.mqtt = None

    def connected(self):
        return self.mqtt is not None
