import PyFlow
from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *
import pydantic
from robinson.messaging.mqtt import MQTTConnection
from robinson_ryven.robinson.base import RobinsonWrapperMixin
from robinson_ryven.robinson.executor import TopicRegistry
from robinson_ryven.robinson.nodes.components import PrintOutputComponent

from robinson_ryven.robinson.utils import getNodeLogger

from robinson.components import Component, InputOutputPortComponent

from functools import partial

from blinker import Signal

from PyFlow.Core import NodeBase
from PyFlow.Core.Common import *
import vebas.config

config = vebas.config.default_config()
vebas.config.default_logging_settings()

class ExternalSource(NodeBase):

    _packageName = "robinson"

    connections:dict = {}

    def __init__(self, name, uid=None):
        super().__init__(name, uid=uid)
        self.logger = getNodeLogger(self)

        self.topic = "out"

        self.topic_reg = TopicRegistry()
        self.mqtt = MQTTConnection("mqtt", config["mqtt"]["server_uri"])
        self.mqtt.init()

        self.outp = self.createOutputPin(self.topic, "AnyPin", None)
        self.outp.enableOptions(PinOptions.AllowAny)

        self.init_ports()

    def update_topic(self, topic):
        self.topic = topic
        self.outp.setName(topic, force=True)

        self.init_ports()

    def receive_msg(self, msg):
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
        transformer.connect(self.receive_msg)

        self.connections[global_id] = transformer
        mqtt_port.connect(transformer)

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


# class graphOutputs(NodeBase):
#     """Represents a group of output pins on compound node
#     """
#     def __init__(self, name):
#         super(graphOutputs, self).__init__(name)
#         self.bCacheEnabled = False

#     def getUniqPinName(self, name):
#         result = name
#         graphNodes = self.graph().getNodesList(classNameFilters=['graphInputs', 'graphOutputs'])
#         conflictingPinNames = set()
#         for node in graphNodes:
#             for pin in node.pins:
#                 conflictingPinNames.add(pin.name)
#         result = getUniqNameFromList(conflictingPinNames, name)
#         return result

#     @staticmethod
#     def category():
#         return 'SubGraphs'

#     @staticmethod
#     def keywords():
#         return []

#     @staticmethod
#     def description():
#         return ''

#     def postCreate(self, jsonTemplate=None):
#         super(graphOutputs, self).postCreate(jsonTemplate=jsonTemplate)
#         # recreate dynamically created pins
#         existingPins = self.namePinInputsMap
#         if jsonTemplate is not None:
#             sortedInputs = sorted(jsonTemplate["inputs"], key=lambda x: x["pinIndex"])
#             for inPinJson in sortedInputs:
#                 if inPinJson['name'] not in existingPins:
#                     inDyn = self.addInPin(inPinJson['name'], inPinJson["dataType"])
#                     inDyn.uid = uuid.UUID(inPinJson['uuid'])

#     def addInPin(self, name=None, dataType="AnyPin"):
#         if name is None:
#             name = self.getUniqPinName('out')
#         p = self.createInputPin(name, dataType, constraint=name, structConstraint=name, structure=StructureType.Multi)
#         p.enableOptions(PinOptions.RenamingEnabled | PinOptions.Dynamic)
#         if dataType == "AnyPin":
#             p.enableOptions(PinOptions.AllowAny | PinOptions.DictElementSupported)
#         return p

#     def compute(self, *args, **kwargs):
#         compoundNode = None
#         for i in self.inputs.values():
#             for o in i.affects:
#                 compoundNode = o.owningNode()
#                 o.setDirty()
#         if compoundNode:
#             compoundNode.processNode()
