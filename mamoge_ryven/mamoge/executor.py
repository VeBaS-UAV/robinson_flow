#!/usr/bin/env python3

import threading
import time
from ryvencore.FlowExecutor import FlowExecutor
from vebas.messaging.mqtt.serializer import JsonTransform

from . import nodes
import importlib
import vebas.config
from functools import partial

from vebas.messaging.mqtt import MQTTConnection
config = vebas.config.default_config()
vebas.config.default_logging_settings()

class RobinsonFlowExecutor(FlowExecutor):

    json_transformers = {}

    def __init__(self, flow):
        self.logger = vebas.config.getLogger(self)
        self.flow = flow
        self.running = False
        self.thread = None
        self.mqtt = MQTTConnection("mqtt", config["mqtt"]["server_uri"])
        self.mqtt.init()

        self.ext_sources = [n for n in self.flow.nodes if isinstance(n,nodes.ExternalSource)]
        self.ext_sink = [n for n in self.flow.nodes if isinstance(n,nodes.ExternalSink)]

        for es in self.ext_sources:
            self.register_external_source(es)

        for es in self.ext_sink:
            self.register_external_sink(es)

    def register_external_source(self,node):
        topic = node.get_topic()
        self.mqtt.mqtt_output(topic) >> partial(self.call_external_source, node)
        print("register topic ", topic)
        return

    def register_external_sink(self,node):
        topic = node.get_topic()

        if topic is None:
            print("Topic is none for sink ", node)
            return
        print("Register sink for topic ", topic)
        node.external_output.connect(partial(self.receive_from_external_sink, node, topic))

    def call_external_source(self, node, msg):
        print("call_external_source", node, msg)

        topic_type = node.get_topic_type()

        if topic_type is not None and len(topic_type) > 0:
            if topic_type not in self.json_transformers:
                if topic_type.find(".") >= 1:
                    module_name, class_name = topic_type.rsplit(".",1)
                    module = importlib.import_module(module_name)
                    cls = getattr(module, class_name)
                    self.json_transformers[topic_type] = JsonTransform(cls)
                else:
                    cls = eval(topic_type)
                    self.json_transformers[topic_type] = JsonTransform(cls)
            json_transform = self.json_transformers[topic_type]
        else:
            json_transform = JsonTransform()

        node.set_output_val(0,json_transform.json_transform(msg))

    def receive_from_external_sink(self, es, topic, msg):
        print("Received from external sink", topic, msg)

        self.mqtt.publish(topic, msg)


    def node_added(self, node):
        if isinstance(node, nodes.ExternalSource):
            node.topic_changed.connect(self.register_external_source)

        if isinstance(node, nodes.ExternalSink):
            node.topic_changed.connect(self.register_external_sink)

    def node_removed(self, node):
        if isinstance(node, nodes.ExternalSource):
            topic = node.get_topic()
            print("TODO unregister topic ", topic)
            return

        if isinstance(node, nodes.ExternalSink):
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
        self.mqtt.cleanup()


    def step(self):

        if True:
            return

        node_stack = queue.Queue()
        nodes = filter(lambda n: len(n.inputs)==0 or all([len(p.connections)==0 for p in n.inputs]),self.flow.nodes)

        call_set = set()

        for n in nodes:
            node_stack.put(n)
            call_set.add(n)


        # print("executing stack on queue", node_stack, node_stack.empty())
        while not node_stack.empty():
            n = node_stack.get(block=False)
            # print("Call update on node ", n)
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
