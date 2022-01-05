#!/usr/bin/env python3
from ryvencore import dtypes
from ryvencore.NodePortBP import NodeInputBP, NodeOutputBP
import ryvencore_qt as rc
from random import random

import traceback as tb
import ipdb
from functools import partial
# let's define some nodes
# to easily see something in action, we create one node generating random numbers, and one that prints them

from vebas.components.common import DebugOutput
from vebas.components import Component, DataPortOutput, InputOutputPortComponent

import vebas.config
vebas.config.default_logging_settings()

import logging

from PyQt5.QtCore import pyqtSignal


# cl = InputOutputPortComponent
def getlogger(cl, name=None):
    fullname = ".".join([type(cl).__module__, type(cl).__name__])
    if name:
        fullname += f".{name}"
    return logging.getLogger(fullname)

from ryvencore_qt.src.flows.nodes.PortItemInputWidgets import Data_IW_M as Data_IW

import widgets

class TestComponent(InputOutputPortComponent):

    def __init__(self, name):
        super(TestComponent, self).__init__(name)
        self.dataport_output_test = DataPortOutput("testout")

        self.testinput = None
        self.defaultinput = None

    def dataport_input(self, msg):
        self.logger.info("Received defaultinput %s", msg)
        self.defaultinput = msg

    def dataport_input_testinput(self, msg):
        self.logger.info("Received testinput %s", msg)
        self.testinput = msg

    def update(self):
        self.logger.info("Textcomponent update")

        if self.defaultinput is not None:
            self.logger.info("call defaultport")
            self.dataport_output(self.defaultinput)
            self.defaultinput = None
        if self.testinput is not None:
            self.logger.info("call testport")
            self.dataport_output_test(self.testinput)
            self.testinput = None


class PrintOutputComponent(Component):

    def __init__(self, name: str):
        super().__init__(name)
        self.msg = None

    def dataport_input_msg(self, msg):
        self.msg = msg


    def update(self):
        if self.msg:
            self.logger.info(f"received msg: {self.msg}")
            self.msg = None


class MamoGeRyvenNode(rc.Node):

    def __init__(self, params):
        super().__init__(params)

            
    # def update(self, inp=-1):
    #     # print("update", inp)
    #     #return super().update(inp=inp)
    #     #do not propagate update, executor will do it
    #     return


class MamoGeRyvenWrapper(MamoGeRyvenNode):

    def __init__(self, component, params):
        super().__init__(params)
        self.component = component(self.title)

        self.input_wires = []
        self.output_wires = []

    def call_input_port_by_name(self, name, *args, **kw_args):
        # print("call_input_port_by_name", name, args, kw_args)
        getattr(self.component, name)(*args, **kw_args)

    def call_output_port_by_index(self, index, *args, **kw_args):
        # print("call outputport by index", index, args, kw_args)
        self.outputs[index].set_val(args[0])

    def cl_input_ports(self, cl):
        return [f for f in cl.__class__.__dict__.keys() if f.startswith("dataport_input")]

    def cl_output_ports(self, cl):
        return [f for f in cl.__dict__.keys() if f.startswith("dataport_output")]

    def setup_ports(self, inputs_data=None, outputs_data=None):
        # overwrite default port creation
        #
        input_ports = self.cl_input_ports(self.component)
        output_ports = self.cl_output_ports(self.component)

        for port_name in input_ports:
            port_index = len(self.inputs)
            self.create_input(port_name[port_name.rfind("_")+1:])
            # print("creating input port at index ", port_index)
            self.input_wires.append(partial(self.call_input_port_by_name, port_name))

        for output_port in output_ports:
            port_index = len(self.outputs)
            # print("create output wirde for index", port_index, output_port)
            self.create_output(output_port[output_port.rfind("_")+1:])
            # getattr(self.component, output_port).connect(lambda *args, **kw_args: self.outputs[port_index].set_val(*args, **kw_args))
            # getattr(self.component, output_port).connect(lambda *args, **kw_args: self.outputs[port_index].set_val(args[0]))
            getattr(self.component, output_port).connect(partial(self.call_output_port_by_index, port_index))

    # def update(self, inp=-1):
    #     # print("update", inp)
    #     # if inp >= 0:
    #         # print("call input wires", inp)
    #         # self.input_wires[inp](self.input(inp))
    #     super().update(inp)
    #     return


    def update_event(self, inp=-1):
        # print("update event")
        self.component.update()


class TestNode(MamoGeRyvenWrapper):
    """Prints your data"""
    title = "Test"
    # we could also skip the constructor here
    def __init__(self, params):
        super().__init__(TestComponent, params)

class PrintNode(MamoGeRyvenWrapper):
    """Prints your data"""
    title = "Print"
    # we could also skip the constructor here
    def __init__(self, params):
        super().__init__(PrintOutputComponent, params)

class ExternalSource(MamoGeRyvenNode):

    title = "External Source"
    color = '#e06c78'
    # this one gets automatically created once for each object
    main_widget_class = widgets.ExternalSourceWidget
    main_widget_pos = 'between ports'  # alternatively 'between ports'
    # main_widget_pos = 'below ports'  # alternatively 'between ports'

    topic_changed = pyqtSignal(rc.Node)
    # you can use those for your data inputs
    # input_widget_classes = {
        # 'topic_widget': widgets.ExternalSourceInputTopicWidget
    # }

    init_inputs = [
        # NodeInputBP(label='', add_data={'widget name': 'topic_widget', 'widget pos': 'besides'})
        # NodeInputBP(label='')
    ]

    init_outputs = [
        NodeOutputBP(label='')
    ]

    def __init__(self, params):
        super().__init__(params)
        self.logger = getlogger(self)
        self.topic = None
        self.topic_type = None

    def get_topic(self):
        return self.topic

    def get_topic_type(self):
        return self.topic_type

    def set_topic(self, topic):
        self.topic = topic
        self.topic_changed.emit(self)

    def set_topic_type(self, topic):
        self.topic_type = topic
        # self.topic_changed.emit(self)

class ExternalSink(MamoGeRyvenNode):

    title = "External Sink"
    color = '#DC8665'
    # this one gets automatically created once for each object
    main_widget_class = widgets.ExternalSinkWidget
    main_widget_pos = 'between ports'  # alternatively 'between ports'

    topic_changed = pyqtSignal(rc.Node)
    # you can use those for your data inputs
    input_widget_classes = {
        # 'topic_widget': widgets.ExternalSinkTopicWidget
    }

    init_inputs = [
        # NodeInputBP(label='', add_data={'widget name': 'topic_widget', 'widget pos': 'besides'})
        NodeInputBP(label='')
    ]

    init_outputs = [
        # NodeOutputBP(label='')
    ]

    external_output = pyqtSignal(object)

    def __init__(self, params):
        super().__init__(params)
        self.logger = getlogger(self)

        # self.create_input("topic", add_data={'widget name': 'my inp widget', 'widget pos': 'beside'})
        # self.create_output("output")

        self.topic = None

    def get_topic(self):
        return self.topic

    def set_topic(self, topic):
        self.topic = topic
        self.topic_changed.emit(self)


    def update_event(self, inp=-1):
        print("sink update", self.input(0))
        self.external_output.emit(self.input(0))

class RandNodeRyven(rc.Node):
    """Generates scaled random float values"""

    title = 'Rand(ryven)'
    init_inputs = [
        rc.NodeInputBP(dtype=rc.dtypes.Data(default=1)),
    ]
    init_outputs = [
        rc.NodeOutputBP(),
    ]
    color = '#fcba03'

    def update_event(self, inp=-1):
        print("RandNodeRyven update event")
        # random float between 0 and value at input
        val = random() * self.input(0)

        # setting the value of the first output
        self.set_output_val(0, val)

class PrintNodeRyven(rc.Node):
    title = 'Print(ryven)'
    init_inputs = [
        NodeInputBP(),
    ]
    color = '#A9D5EF'

    def update_event(self, inp=-1):
        print("PrintNodeRyven update_event", type(self.input(0)), self.input(0))

def export_nodes():

    return [
        PrintNode,
        TestNode,
        RandNodeRyven,
        PrintNodeRyven,
        ExternalSource,
        ExternalSink
    ]
