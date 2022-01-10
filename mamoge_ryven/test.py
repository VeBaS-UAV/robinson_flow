#!/usr/bin/env python3

from robinson.components.common import DebugOutput
from robinson.components import DataPortOutput, InputOutputPortComponent

# cl = InputOutputPortComponent

class TestComponent(InputOutputPortComponent):

    def __init__(self, name):
        super(TestComponent, self).__init__(name)
        self.dataport_output_test = DataPortOutput("testout")

    def dataport_input_testinput(self, msg):
        print("Received testinput")

def cl_input_ports(cl):
    return [f for f in cl.__class__.__dict__.keys() if f.startswith("dataport_input")]

def cl_output_ports(cl):
    return [f for f in cl.__dict__.keys() if f.startswith("dataport_output")]

tc = TestComponent('Hello')

# %%

cl_input_ports(tc)

cl_output_ports(tc)
