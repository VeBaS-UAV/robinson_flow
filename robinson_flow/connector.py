#!/usr/bin/env python3
from robinson.messaging.mqtt import MQTTConnection
import robinson_flow
from robinson.messaging.mqtt import MQTTConnection
import vebas.config
from pymavlink.dialects.v20.ardupilotmega import MAVLink_message
from robinson.messaging.mqtt.serializer import Image, JsonTransform
from vebas.taskplanner.types import Seedling, SeedlingsList

class EnvironmentConnector():

    def output_port(self, topic):
        raise NotImplementedError()

    def input_port(self, topic):
        raise NotImplementedError()

class MQTTConnector(EnvironmentConnector):
    def __init__(self, settings):
        self.logger = vebas.config.getLogger(self)
        self.mqtt = MQTTConnection("mqtt", settings.server)
        self.mqtt.init()

    def output_port(self, topic):
        self.logger.info(f"connect {topic}")
        mqtt_port = self.mqtt.mqtt_output(topic)
        return mqtt_port

    def input_port(self, topic):
        self.logger.info(f"connect {topic}")
        mqtt_port = self.mqtt.mqtt_input(topic)
        return mqtt_port

    def cleanup(self):
        self.mqtt.cleanup()


class TopicRegistryItem():

    def __init__(self, msg_type, transformer, *args, **kwargs) -> None:
        self.msg_type = msg_type
        self.transformer = transformer
        self.args = args
        self.kwargs = kwargs

    def create(self):
        return self.transformer(*self.args, **self.kwargs)


class TopicRegistry():

    registry = {}

    def __init__(self, topic_mapping = {}) -> None:

        self.registry = topic_mapping

        # for topic, (msg_type, transformer, args) in topic_mapping:
            # self.registry[topic] = TopicRegistryItem(msg_type, transformer, args)

        self.registry["default"] = TopicRegistryItem(dict, JsonTransform)

    def find(self, topic:str) -> TopicRegistryItem:
        import fnmatch

        for key, item in self.registry.items():
            if fnmatch.fnmatch(topic, key):
                return item

        return self.registry["default"]

    def is_valid_topic(self, topic):
        return True if topic is not None and len(topic) > 0 else False


class ExternalConnectionHandler():

    def __init__(self, settings) -> None:
        self.logger = vebas.config.getLogger(self)
        self.config = settings

        self.registry = {}
        self.registry["mavlink"] = TopicRegistryItem(MAVLink_message, JsonTransform, MAVLink_message)
        self.registry["mavlink/*"] = TopicRegistryItem(MAVLink_message, JsonTransform, MAVLink_message)
        self.registry['vebas/uav/camera/image'] = TopicRegistryItem(Image, JsonTransform, Image)
        self.registry['vebas/**/image'] = TopicRegistryItem(Image, JsonTransform, Image)
        self.registry['vebas/taskplanner/seedlings'] = TopicRegistryItem(SeedlingsList, JsonTransform, SeedlingsList)
        self.registry["*"] = TopicRegistryItem(dict, JsonTransform)
        self.registry["default"] = TopicRegistryItem(dict, JsonTransform)
        self.topic_registry = TopicRegistry(self.registry)
        self.mqtt = MQTTConnection("robinson.mqtt", self.config.mqtt.server)

        self.mqtt.init()

    def external_source(self, topic):
        self.logger.info(f"exteral_source for topic {topic}")
        mqtt_port = self.mqtt.mqtt_output(topic)
        reg_item = self.topic_registry.find(topic)
        transformer = reg_item.create()
        mqtt_port.connect(transformer)
        return transformer

    def external_sink(self, topic):
        self.logger.info(f"exteral_sink for topic {topic}")
        mqtt_port = self.mqtt.mqtt_input(topic)
        reg_item = self.topic_registry.find(topic)
        transformer = reg_item.create()
        transformer.connect(mqtt_port)
        return transformer.to_json
