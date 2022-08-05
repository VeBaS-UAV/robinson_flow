import PyFlow
from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *
import pydantic
from robinson.messaging.mqtt import MQTTConnection
from robinson_flow.connector import ExternalConnectionHandler, TopicRegistry, TopicRegistryItem

from robinson.components import Component, InputOutputPortComponent

from functools import partial

from blinker import Signal

from PyFlow.Core import NodeBase
from PyFlow.Core.Common import *

from Qt.QtCore import QObject, Signal

from robinson_flow.logger import getNodeLogger

class ExternalBase(NodeBase):
    _packageName = "robinson"
    connections:dict = {}

    external_connection = None
    def __init__(self, name, uid=None):
        super().__init__(name, uid)
        self.logger = getNodeLogger(self)

        self.topic = "topic_name"

        self.ext_con = ExternalConnectionHandler.instance()

    def serialize(self):
        data =  super().serialize()
        data["topic"] = self.topic
        return data

    def postCreate(self, jsonTemplate={}):
        super().postCreate(jsonTemplate)

        if "topic" in jsonTemplate:
            self.update_topic(jsonTemplate["topic"])

    def deserialize(self, jsonData):
        return super().deserialize(jsonData)

class ExternalSource(ExternalBase,QObject):

    _packageName = "robinson"

    msg_received_signal = Signal()

    def __init__(self, name, uid=None):
        super().__init__(name, uid=uid)

        self.outp = self.createOutputPin(self.topic, "AnyPin", None)
        self.outp.enableOptions(PinOptions.AllowAny)

        self.msg_buffer = None
        self.msg_received_signal.connect(self.received_msg_slot)

        self.init_ports()

    def received_msg_slot(self):
        if self.msg_buffer is not None:
            self.outp.setData(self.msg_buffer)
            self.msg_buffer = None

    def receive_msg(self, msg):
        tp = type(msg)
        self.msg_buffer = msg
        self.msg_received_signal.emit()

        # if tp.__name__ == "Image":
            # self.logger.error("Received Image")
            #
        # def callback():
            # print("Callback call qtimer")

        # QTimer.singleShot(1, callback)

    def init_ports(self):

        global_id = self.uid

        if global_id in self.connections:
            # mqtt_port.disconnect(self.connections[global_id])
            self.connections[global_id].cleanup()
            del self.connections[global_id]

        mqtt_port = self.ext_con.external_source(self.topic)
        mqtt_port.connect(self.receive_msg)
        self.connections[global_id] = mqtt_port

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
        self.inp.enableOptions(PinOptions.AllowMultipleConnections)
        self.inp.dataBeenSet.connect(self.compute)

        self.output_port = None
        self.init_ports()

    def init_ports(self):

        mqtt_port = self.ext_con.external_sink(self.topic)

        global_id = self.uid

        if global_id in self.connections:
            self.connections[global_id].cleanup()
            del self.connections[global_id]

        self.output_port = mqtt_port

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

