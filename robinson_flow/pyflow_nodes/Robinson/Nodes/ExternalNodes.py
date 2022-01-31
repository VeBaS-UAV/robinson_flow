import PyFlow
from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *
import pydantic
from robinson.messaging.mqtt import MQTTConnection
from robinson_flow.ryven_nodes.base import RobinsonWrapperMixin
from robinson_flow.ryven_nodes.executor import TopicRegistry
from robinson_flow.ryven_nodes.nodes.components import PrintOutputComponent

from robinson_flow.ryven_nodes.utils import getNodeLogger

from robinson.components import Component, InputOutputPortComponent

from functools import partial

from blinker import Signal

from PyFlow.Core import NodeBase
from PyFlow.Core.Common import *
import vebas.config


from PyQt5.QtCore import pyqtSignal, QObject

from robinson_flow.config import settings
# config = vebas.config.default_config()
vebas.config.default_logging_settings()


class ExternalBase(NodeBase):
    _packageName = "robinson"
    connections:dict = {}

    def __init__(self, name, uid=None):
        super().__init__(name, uid)
        self.logger = getNodeLogger(self)

        self.topic = "topic_name"

        self.topic_reg = TopicRegistry()
        self.mqtt = MQTTConnection("robinson.mqtt", settings.environment.mqtt.server)
        self.mqtt.init()


    def serialize(self):
        data =  super().serialize()
        data["topic"] = self.topic
        # self.logger.info(f"serialize {data}")
        return data

    def postCreate(self, jsonTemplate=None):
        super().postCreate(jsonTemplate)

        if "topic" in jsonTemplate:
            self.update_topic(jsonTemplate["topic"])

    def deserialize(self, jsonData):
        return super().deserialize(jsonData)

class ExternalSource(ExternalBase,QObject):

    _packageName = "robinson"

    # msg_signal = pyqtSignal(object)

    def __init__(self, name, uid=None):
        super().__init__(name, uid=uid)

        self.outp = self.createOutputPin(self.topic, "AnyPin", None)
        self.outp.enableOptions(PinOptions.AllowAny)

        self.init_ports()

        # self.msg_signal.connect(self.receive_msg)

    def receive_msg(self, msg):
        tp = type(msg)
        # self.logger.info(f"reveive_msg {msg}"[:20])
        self.outp.setData(msg)

    def init_ports(self):
        mqtt_port = self.mqtt.mqtt_output(self.topic)

        global_id = self.uid

        if global_id in self.connections:
            mqtt_port.disconnect(self.connections[global_id])
            self.connections[global_id].cleanup()
            del self.connections[global_id]

        reg_item = self.topic_reg.find(self.topic)

        transformer = reg_item.create()
        # transformer.connect(self.msg_signal.emit)
        transformer.connect(self.receive_msg)

        self.connections[global_id] = transformer
        mqtt_port.connect(transformer)

    def update_topic(self, topic):
        self.topic = topic
        self.outp.setName(topic, force=True)

        self.init_ports()

    def compute(self, *args, **kwargs):
        pass

    @staticmethod
    def pinTypeHints():
        helper = NodePinsSuggestionsHelper()
        return helper

    @staticmethod
    def category():
        return 'extern'

    @staticmethod
    def keywords():
        return []

    @staticmethod
    def description():
        return "Description in rst format."

class ExternalSink(ExternalBase):

    def __init__(self, name, uid=None):
        super().__init__(name, uid=uid)

        self.topic = "in"

        self.inp = self.createInputPin(self.topic, "AnyPin", None)
        self.inp.enableOptions(PinOptions.AllowAny)
        self.inp.dataBeenSet.connect(self.compute)

        self.output_port = None
        self.init_ports()

    def init_ports(self):

        reg_item = self.topic_reg.find(self.topic)

        mqtt_port = self.mqtt.mqtt_input(self.topic)

        global_id = self.uid

        if global_id in self.connections:
            self.connections[global_id].cleanup()
            del self.connections[global_id]

        transformer = reg_item.create()
        self.connections[global_id] = transformer

        transformer.connect(mqtt_port)
        # node.external_output.connect(transformer)
        self.output_port = transformer.to_json

    def update_topic(self, topic):
        self.topic = topic
        self.inp.setName(topic, force=True)

        self.init_ports()

    def compute(self, *args, **kwargs):
        if self.inp.dirty == True and self.output_port is not None:
            self.output_port(self.inp.getData())

    @staticmethod
    def pinTypeHints():
        helper = NodePinsSuggestionsHelper()
        return helper

    @staticmethod
    def category():
        return 'extern'

    @staticmethod
    def keywords():
        return []

    @staticmethod
    def description():
        return "Description in rst format."

