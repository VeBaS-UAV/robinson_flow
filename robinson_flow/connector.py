#!/usr/bin/env python3
from robinson.messaging.mqtt import MQTTConnection
from robinson.messaging.mqtt import MQTTConnection
from pymavlink.dialects.v20.ardupilotmega import MAVLink_message
from robinson.messaging.mqtt.serializer import Image, JsonTransform
# from vebas.taskplanner.types import Seedling, SeedlingsList

from robinson_flow.logger import getLogger
import copy

class EnvironmentConnector():

    def output_port(self, topic):
        raise NotImplementedError()

    def input_port(self, topic):
        raise NotImplementedError()

class MQTTConnector(EnvironmentConnector):
    def __init__(self, settings):
        self.logger = getLogger(self)
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

    def __init__(self, topic, msg_type, transformer, *args, **kwargs) -> None:
        self.topic = topic
        self.msg_type = msg_type
        self.transformer = transformer
        self.args = args
        self.kwargs = kwargs

    def create(self):
        return self.transformer(*self.args, **self.kwargs)


class TopicRegistry():

    registry = {}

    def __init__(self, default:TopicRegistryItem,  topic_mapping = {}) -> None:
        self.default_item:TopicRegistryItem = default
        self.registry = topic_mapping

    def find(self, key:str) -> TopicRegistryItem:
        import re

        if key == "uav_camera_down":
            pass
        for pattern, item in self.registry.items():
            match = re.fullmatch(pattern,key)

            if match:
                topic = item.topic.format(*match.groups(),**match.groupdict())

                ii = copy.copy(item)

                ii.topic = topic

                return ii

        # raise BaseException(f"Could not find {key}")
        return self.default_item

    def is_valid_topic(self, topic):
        return True if topic is not None and len(topic) > 0 else False


class ExternalConnectionHandler():

    def __init__(self, settings) -> None:
        self.logger = getLogger(self)
        self.config = settings

        self.registry = {}
        self.registry[r"mavlink"] = TopicRegistryItem("mavlink", MAVLink_message, JsonTransform, MAVLink_message)
        self.registry[r"mavlink/(?P<name>.*)"] = TopicRegistryItem("mavlink/{name}", MAVLink_message, JsonTransform, MAVLink_message)
        self.registry[r"mavlink_(?P<name>.*)"] = TopicRegistryItem("mavlink/{name}", MAVLink_message, JsonTransform, MAVLink_message)
        self.registry[r"uav_camera_down"] = TopicRegistryItem("vebas/uav/camera/image", Image, JsonTransform, Image)
        self.registry[r"tracking_image"] = TopicRegistryItem("vebas/uav/tracking/image", Image, JsonTransform, Image)
        # self.registry['vebas/**/image'] = TopicRegistryItem(Image, JsonTransform, Image)
        self.registry[r"seedling_position/(.*)"] = TopicRegistryItem("vebas/tracking/{0}", dict, JsonTransform)
        self.registry['vebas_seedlingslist'] = TopicRegistryItem("vebas/taskplanner/seedlings", dict, JsonTransform)

        default_item = TopicRegistryItem("NOT_DEFINED_{0}", dict, JsonTransform)
        # self.registry["default"] = TopicRegistryItem(dict, JsonTransform)
        self.topic_registry = TopicRegistry(default_item, self.registry)
        self.mqtt = MQTTConnection("robinson.mqtt", self.config.mqtt.server)

        self.mqtt.init()

    def external_source(self, topic):
        self.logger.info(f"exteral_source for topic {topic}")
        reg_item = self.topic_registry.find(topic)
        mqtt_port = self.mqtt.mqtt_output(reg_item.topic)
        transformer = reg_item.create()
        mqtt_port.connect(transformer)
        return transformer

    def external_sink(self, topic):
        self.logger.info(f"exteral_sink for topic {topic}")
        reg_item = self.topic_registry.find(topic)
        mqtt_port = self.mqtt.mqtt_input(reg_item.topic)
        transformer = reg_item.create()
        transformer.connect(mqtt_port)
        return transformer.to_json
