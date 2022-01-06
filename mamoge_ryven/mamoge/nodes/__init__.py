#!/usr/bin/env python3
from ryvencore.NodePortBP import NodeInputBP, NodeOutputBP
from random import random

import ryvencore_qt as rc
# let's define some nodes
# to easily see something in action, we create one node generating random numbers, and one that prints them

from vebas.components import Component, DataPortOutput, InputOutputPortComponent

import vebas.config
from mamoge_ryven import mamoge

from mamoge_ryven.mamoge.base import MamoGeRyvenWrapper

from .external_sources import *
from .components import export_nodes as component_nodes

# from mamoge_ryven.mamoge.nodes import MamoGeRyvenNode, MamoGeRyvenWrapper
vebas.config.default_logging_settings()

from ryvencore_qt.src.flows.nodes.PortItemInputWidgets import Data_IW_M as Data_IW

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

    nodes = []

    nodes.extend([
        ExternalSource,
        ExternalSink
    ])

    nodes.extend(component_nodes())


    return nodes
