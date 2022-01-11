#!/usr/bin/env python3

import inspect
import threading
import time
from pymavlink.dialects.v20.ardupilotmega import MAVLink_message
from ryvencore.FlowExecutor import FlowExecutor
from robinson.messaging.mqtt.serializer import JsonTransform

from robinson_ryven.robinson.base import RobinsonRyvenNode, RobinsonRyvenWrapper
from robinson_ryven.robinson import base
from robinson_ryven.robinson.nodes.external_sources import ExternalSink, ExternalSource

from . import nodes
import vebas.config

from robinson.messaging.mqtt import MQTTConnection
config = vebas.config.default_config()
vebas.config.default_logging_settings()
import queue

from robinson_ryven.robinson.utils import getLogger

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

    def __init__(self) -> None:

        self.registry["mavlink/*"] = TopicRegistryItem(MAVLink_message, JsonTransform, MAVLink_message)
        self.registry["*"] = TopicRegistryItem(dict, JsonTransform)
        self.registry["default"] = TopicRegistryItem(dict, JsonTransform)

    def find(self, topic:str) -> TopicRegistryItem:
        import fnmatch

        for key, item in self.registry.items():
            if fnmatch.fnmatch(topic, key):
                return item

        return self.registry["default"]

    def is_valid_topic(self, topic):
        return True if topic is not None and len(topic) > 0 else False

class ExternalSourceConnector():


    connections:dict = {}

    def __init__(self, topic_registry:TopicRegistry):
        self.logger = getLogger(self)

        self.topic_reg = topic_registry
        self.mqtt = MQTTConnection("mqtt", config["mqtt"]["server_uri"])
        self.mqtt.init()

    def connect_topic_to_node(self, topic, node:RobinsonRyvenNode):

        self.logger.info(f"connect {topic} to {node}")
        # self.logger.info(f"connect topic to node {node.ID}, {node.GLOBAL_ID}")

        mqtt_port = self.mqtt.mqtt_output(topic)

        global_id = node.GLOBAL_ID

        if global_id in self.connections:
            mqtt_port.disconnect(self.connections[global_id])
            self.connections[global_id].cleanup()
            del self.connections[global_id]

        reg_item = self.topic_reg.find(topic)

        transformer = reg_item.create()
        transformer.connect(node.receive_msg)

        self.connections[global_id] = transformer
        mqtt_port.connect(transformer)



    def connect_node_to_topic(self, node, topic):
        reg_item = self.topic_reg.find(topic)

        mqtt_port = self.mqtt.mqtt_input(topic)

        global_id = node.GLOBAL_ID

        if global_id in self.connections:
            self.connections[global_id].cleanup()
            del self.connections[global_id]

        transformer = reg_item.create()
        self.connections[global_id] = transformer

        transformer.connect(mqtt_port)
        node.external_output.connect(transformer)

    def cleanup(self):
        self.mqtt.cleanup()

class RobinsonFlowExecutor(FlowExecutor):

    json_transformers = {}

    def __init__(self, flow, config):
        self.logger = vebas.config.getLogger(self)
        self.config = config
        self.flow = flow
        self.running = False
        self.thread = None
        self.topic_registry = TopicRegistry()

        self.external_source_connector = ExternalSourceConnector(self.topic_registry)

        self.ext_sources = [n for n in self.flow.nodes if isinstance(n,ExternalSource)]
        self.ext_sink = [n for n in self.flow.nodes if isinstance(n,ExternalSink)]

        for es in self.ext_sources:
            self.register_external_source(es)

        for es in self.ext_sink:
            self.register_external_sink(es)

        [self.init_node(n) for n in self.flow.nodes if isinstance(n,RobinsonRyvenWrapper)]

        [n.reinit_node.connect(self.init_node) for n in self.flow.nodes if isinstance(n,RobinsonRyvenWrapper)]

    def register_external_source(self,node):
        self.logger.info(f"register external source for node {node}")
        topic = node.get_topic()
        if self.topic_registry.is_valid_topic(topic):
            self.external_source_connector.connect_topic_to_node(topic, node)
            self.logger.info(f"Register external source for topic {topic}")

    def register_external_sink(self,node):
        self.logger.info(f"register external sink for node {node}")
        topic = node.get_topic()
        if self.topic_registry.is_valid_topic(topic):
            self.external_source_connector.connect_node_to_topic(node, topic)
            self.logger.info(f"Register external sink for topic {topic}")

    def node_added(self, node):
        self.logger.info(f"node_added {node}")
        if isinstance(node, ExternalSource):
            self.logger.info(f"node_added ExternalSource for node {node}")
            node.topic_changed.connect(self.register_external_source)

        if isinstance(node, ExternalSink):
            self.logger.info(f"node_added ExternalSink for node {node}")
            node.topic_changed.connect(self.register_external_sink)

        if isinstance(node, RobinsonRyvenNode):
            node.reinit_node.connect(self.init_node)
            self.init_node(node)

    def node_removed(self, node):
        if isinstance(node, ExternalSource):
            topic = node.get_topic()
            print("TODO unregister topic ", topic)
            return

        if isinstance(node, ExternalSink):
            topic = node.get_topic()
            print("TODO unregister sink")


    # Node.update() =>
    def update_node(self, node, inp):
        print("flow update_node", node, inp)
        pass

    # Node.input() =>
    def input(self, node, index):
        print("flow input", node, index)
        pass

    # Node.set_output_val() =>
    def set_output_val(self, node, index, val):
        print("flow output", node, index, val)
        pass

    # Node.exec_output() =>
    def exec_output(self, node, index):
        print("flow exec output", node, index)
        pass


    def init_node(self, node):
        self.logger.info(f"init_node component {node.display_title}")
        config_args = {}
        name = node.display_title.lower()

        # if name in self.config:
        #     config_args = self.config[name]
        #     self.logger.info(f"Loading config {config_args}")
        # else:
        #     self.logger.warn(f"Could not find config for component {name}")
        # try:
        #     node.init(**config_args)
        # except Exception as e:
        #     self.logger.error(f"Could not init component {node}")
        #     self.logger.error(e)

    def start(self):

        self.running = False
        if self.thread:
            self.thread.join()

        self.thread = threading.Thread(target=self.run)

        self.thread.start()

    def run(self):

        self.running = True
        while(self.running):
            self.step()
            time.sleep(0.1)

        self.cleanup()

    def cleanup(self):
        self.running = False
        self.external_source_connector.cleanup()

    def step(self):

        node_stack = queue.Queue()
        nodes = filter(lambda n: len(n.inputs)==0 or all([len(p.connections)==0 for p in n.inputs]),self.flow.nodes)

        call_set = set()

        for n in nodes:
            node_stack.put(n)
            call_set.add(n)


        # print("executing stack on queue", node_stack, node_stack.empty())
        while not node_stack.empty():
            n = node_stack.get(block=False)
            print("Call update on node ", n)
            n.update_event()

            for suc in self.flow.node_successors[n]:
                if suc not in call_set:
                    node_stack.put(suc)
                    call_set.add(suc)
    def stop(self):
        self.running = False

        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
