#!/usr/bin/env python3
from robinson.messaging.mqtt import MQTTConnection
import robinson_flow
from robinson_flow.ryven_nodes.executor import TopicRegistry

from robinson_flow.ryven_nodes.executor import TopicRegistry
from robinson.messaging.mqtt import MQTTConnection
import vebas.config

class ExternalConnectionHandler():

    def __init__(self, mqtt_server) -> None:
        self.logger = vebas.config.getLogger(self)
        self.topic_registry = TopicRegistry()
        self.mqtt = MQTTConnection("robinson.mqtt", mqtt_server)

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
