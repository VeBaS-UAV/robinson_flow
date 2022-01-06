#!/usr/bin/env python3
from ryvencore import dtypes
from ryvencore.NodePortBP import NodeInputBP, NodeOutputBP
from random import random

import ryvencore_qt as rc
import traceback as tb
import ipdb
from functools import partial
# let's define some nodes
# to easily see something in action, we create one node generating random numbers, and one that prints them

from vebas.components.common import DebugOutput
from vebas.components import Component, DataPortOutput, InputOutputPortComponent

import vebas.config

from mamoge_ryven.mamoge.base import MamoGeRyvenNode, MamoGeRyvenWrapper

from .external_sources import *

# from mamoge_ryven.mamoge.nodes import MamoGeRyvenNode, MamoGeRyvenWrapper
vebas.config.default_logging_settings()


from ryvencore_qt.src.flows.nodes.PortItemInputWidgets import Data_IW_M as Data_IW


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
        val = random() * float(self.input(0))

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
