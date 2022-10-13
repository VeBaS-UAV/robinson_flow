#!/usr/bin/env python3
from PyFlow.Core.Common import SingletonDecorator
from robinson import components
from robinson.messaging.mqtt import MQTTConnection
from robinson.messaging.mqtt import MQTTConnection
from pymavlink.dialects.v20.ardupilotmega import MAVLink_message
from robinson.messaging.mqtt.serializer import Image, JsonTransform, NoTransform

# from vebas.taskplanner.types import Seedling, SeedlingsList
from robinson.messaging.mavlink import (
    MavlinkConnection,
    get_mavlink_msg_args,
    get_mavlink_msg_class,
)

from robinson_flow.logger import getLogger
import copy
from robinson.components import InstanceFilter, ComponentRunner, Composite

import importlib


class EnvironmentConnector:
    def output_port(self, topic):
        raise NotImplementedError()

    def input_port(self, topic):
        raise NotImplementedError()


class MQTTConnector(EnvironmentConnector, Composite):
    def __init__(self, server, ns=""):
        Composite.__init__(self, "EnvironmentConnector")
        self.logger = getLogger(self)
        self.namespace = ns
        self.mqtt = MQTTConnection("mqtt", server)

        self.add_component(self.mqtt)

    def fqns_topic(self, topic):
        if topic[0] == "/":
            return topic[1:]

        if self.namespace is not None:
            return f"{self.namespace}/{topic}"

        return topic

    def output_port(self, topic):
        fqn_topic = self.fqns_topic(topic)
        self.logger.info(f"connect {fqn_topic}")
        mqtt_port = self.mqtt.mqtt_output(fqn_topic)
        return mqtt_port

    def input_port(self, topic):
        fqn_topic = self.fqns_topic(topic)
        self.logger.info(f"connect {fqn_topic}")
        mqtt_port = self.mqtt.mqtt_input(fqn_topic)
        return mqtt_port


class MavlinkConnector(EnvironmentConnector, Composite):
    def __init__(self, uri, ns="") -> None:
        Composite.__init__(self, "MavlinkConnector")
        self.mavlink = MavlinkConnection("mavlink")
        self.mavlink.config_update(uri=uri)
        self.add_component(self.mavlink)

    def input_port(self, topic):
        # return super().output_port(topic)
        return self.mavlink.dataport_input_mavlink_msg

    def output_port(self, topic):
        # return super().input_port(topic)
        cls = get_mavlink_msg_class(topic)
        mavlink_filter = InstanceFilter(cls)
        self.mavlink.dataport_output.connect(mavlink_filter)
        return mavlink_filter


class TopicRegistryItem:
    def __init__(
        self, protocol, topic_pattern, msg_type, transformer, *args, **kwargs
    ) -> None:
        self.protocol = protocol
        self.topic_pattern = topic_pattern
        self.topic = None
        self.msg_type = msg_type
        self.transformer = transformer
        self.args = args
        self.kwargs = kwargs

    def create(self):
        return self.transformer(*self.args, **self.kwargs)

    def update_topic(self, *args, **kwargs):
        self.topic = self.topic_pattern.format(*args, **kwargs)


class TopicRegistry:

    registry = {}

    def __init__(self, default: TopicRegistryItem, topic_mapping={}) -> None:
        self.default_item: TopicRegistryItem = default
        self.registry = topic_mapping
        self.logger = getLogger(self)

    def find(self, key: str) -> TopicRegistryItem:
        import re

        for pattern, item in self.registry.items():
            match = re.fullmatch(pattern, key)

            if match:
                new_instance = copy.copy(item)
                new_instance.update_topic(*match.groups(), **match.groupdict())

                return new_instance

        new_instance = copy.copy(self.default_item)
        new_instance.update_topic(key)
        self.logger.warn(
            f"Using default port for {key} resulting in topic {new_instance.topic}"
        )
        return new_instance

    def is_valid_topic(self, topic):
        return True if topic is not None and len(topic) > 0 else False


class ExternalConnectionHandler(Composite):

    _instance = None

    @staticmethod
    def instance():
        if ExternalConnectionHandler._instance is None:
            import robinson.config

            settings = robinson.config.current()

            ns = ""
            if "namespace" in settings:
                ns = settings.namespace
            if "ns" in settings:
                ns = settings.ns
            if "NAMESPACE" in settings:
                ns = settings.namespace
            if "NS" in settings:
                ns = settings.ns

            ExternalConnectionHandler._instance = ExternalConnectionHandler(
                settings.environment, ns=ns
            )

        return ExternalConnectionHandler._instance

    def __init__(self, settings, ns="") -> None:
        super().__init__("ExternalConnectionHandler")
        self.logger = getLogger(self)
        self.namespace = ns
        self.config = settings

        self.connectors = {}

        self.logger.info(f"Creating external connection with namespace: {ns}")

        for name, desc in self.config.connectors.items():
            try:
                desc = {**desc}  # create a copy
                if len(ns) > 0:
                    desc["ns"] = ns
                dparts = desc["class"].split(".")
                module = ".".join(dparts[:-1])
                module = importlib.import_module(module)
                cls = getattr(module, dparts[-1])

                del desc["class"]
                self.connectors[name] = cls, desc
            except Exception as e:
                self.logger.error(f"Could not parse config for {name} with {desc}")
                self.logger.error(e)

        self.connectors["default"] = self.connectors["mqtt"]

        self.registry = {}

        for name, desc in self.config.connections.items():
            try:
                connector = desc["connector"]
                topic = desc["topic"]

                msgtype = eval(desc["msgtype"])

                transform = eval(desc["transform"])

                if "transform_args" in desc:
                    transform_args = eval(desc["transform_args"])
                else:
                    transform_args = None

                tri = TopicRegistryItem(
                    connector, topic, msgtype, transform, transform_args
                )
                self.registry[name] = tri

            except Exception as e:
                self.logger.error("Could not parse connection config")
                self.logger.error(e)

        default_item = TopicRegistryItem("mqtt", "NOT_DEFINED_{0}", dict, JsonTransform)
        self.topic_registry = TopicRegistry(default_item, self.registry)

        # self.runner = ComponentRunner("external_connection_runner", self.connectors.values(), cycle_rate=10)
        # self.runner.start()

        # [self.add_component(c) for c in self.connectors.values()]

    def ensure_connector_init(self, protocol):
        if isinstance(self.connectors[protocol], tuple):
            cls, kw_args = self.connectors[protocol]
            component = cls(**kw_args)
            self.connectors[protocol] = component
            component.init()
            self.add_component(component)

    def fqns_topic(self, topic):

        if True:
            return topic

        if topic[0] == "/":
            return topic[1:]

        if self.namespace is not None and len(self.namespace) > 0:
            return f"{self.namespace}/{topic}"

        return topic

    def external_source(self, topic):
        self.logger.info(f"exteral_source for topic {topic}")

        fqn_topic = self.fqns_topic(topic)
        self.logger.info(f"mapped to fqn {fqn_topic}")

        reg_item = self.topic_registry.find(fqn_topic)

        if reg_item.protocol in self.connectors:
            self.ensure_connector_init(reg_item.protocol)

            connector = self.connectors[reg_item.protocol]
            self.logger.debug(
                f"using protocol {reg_item.protocol} for topic {reg_item.topic}"
            )
        else:
            self.ensure_connector_init("default")
            connector = self.connectors["default"]
            self.logger.warn(
                f"could not find procotol connector for {reg_item.protocol}, using default {connector}"
            )

        transformer = reg_item.create()
        connector.output_port(reg_item.topic).connect(transformer)
        return transformer

    def external_sink(self, topic):
        self.logger.info(f"exteral_sink for topic {topic}")
        fqn_topic = self.fqns_topic(topic)
        self.logger.info(f"mapped to fqn {fqn_topic}")
        reg_item = self.topic_registry.find(fqn_topic)

        if reg_item.protocol in self.connectors:
            self.ensure_connector_init(reg_item.protocol)
            connector = self.connectors[reg_item.protocol]
            self.logger.debug(
                f"using protocol {reg_item.protocol} for topic {reg_item.topic}"
            )
        else:
            self.ensure_connector_init("default")
            connector = self.connectors["default"]
            self.logger.warn(
                f"could not find procotol connector for {reg_item.protocol}, using default {connector}"
            )

        transformer = reg_item.create()
        transformer.connect(connector.input_port(reg_item.topic))
        return transformer
