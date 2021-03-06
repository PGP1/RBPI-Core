"""
module that contains publish logic.
"""
import paho.mqtt.client as mqtt
import json
import jsonschema
import logging
import os
import utility
import datetime
from dotenv import load_dotenv
env_path = './.env'
load_dotenv(dotenv_path=env_path)

BROKER_IP = os.getenv("BROKER_IP")
BROKER_PORT = os.getenv("BROKER_PORT")

schema = utility.loadconfig.load_config()['schema-raspberrypi']


class Publisher:
    """
    Class that contains publish logic. when given a payload and route
    it will publish to the correct route.
    """

    def __init__(self):
        """
        initialises routes that it will publish to, ip address of MP and port.
        """
        self.broker_address = str(BROKER_IP)
        self.port = int(BROKER_PORT)

    def on_publish(self, client, userdata, result):
        """
        function to run on successful publish

        :param client: the client instance for this callback
        :type client: Client
        :param userdata: the private user data as set in Client()
        or user_data_set()
        :type userdata: [type]
        :param result: Data being published
        :type result: String
        """
        print("[Publish] data published \n")
        pass

    def on_disconnect(self, client, userdata, rc):
        """
        function to run on disconnect

        :param client: the mqtt client
        :type client: Client
        :param userdata: the private user data as set in Client()
            or user_data_set()
        :type userdata: [type]
        :param rc: disconnection result
        :type rc: int
        """
        logging.debug("disconnected, rc=", str(rc))
        client.loop_stop()
        print("[Publish] client disconnected OK")

    def publish(self, pub, arduinopayload):
        """
        initialises client and binds functions, publish received payload
        to MP and disconnects.

        :param arduinopayload: the item that's being sent,
            will be converted into json.
        :type json: any
        :param pub: type of payload to publish, status & arduino
        :type pub: string
        """
        print("[Publish] Sending to: ", self.broker_address)
        print("[Publish] on: ", self.port)
        if pub == 'arduino':
            # setting topic to publish to
            topic = utility.loadconfig.load_config()['topic']['toawsiot/b1']
            brokerID = utility.iddevice.get_id()
            now_time = datetime.datetime.now().now().isoformat()

            publishJSON = {}
            payload = {}

            publishJSON['broker-device'] = brokerID
            payload['time'] = now_time
            data = arduinopayload
            payload['data'] = data
            publishJSON['payload'] = payload

            # create new instance
            client = mqtt.Client("awsiot-client")
            client.on_publish = self.on_publish
            client.on_disconnect = self.on_disconnect

            # set broker address of raspberry pis
            # connect to pi
            client.connect(self.broker_address, self.port)

            print(publishJSON)
            try:
                jsonschema.validate(publishJSON, schema)
                # Publish to topic 'localgateway_to_awsiot/b1' for AWS IoT to pickup
                client.publish(topic, json.dumps(publishJSON))
                client.disconnect()
            except Exception as e:
                print("[Error] Not valid json format")
                print('[Error]', e)
        elif pub == 'status':
            # Publish back to the AWSIoT to respond for request for online
            # status
            client = mqtt.Client("awsiot-client-status")
            client.on_publish = self.on_publish
            client.on_disconnect = self.on_disconnect

            client.connect(self.broker_address, self.port)

            topic = loadconfig.load_config()['topic']['toawsiot/b1']
            id = utility.iddevice.get_id()
            payload = {'broker-device': id, 'payload': 'On'}
            client.publish(topic, json.dumps(payload))
            client.disconnect()
