#!/usr/bin/env python3

from robinson.components import Component, DataPortOutput, OutputPortComponent
from robinson_flow.pyflow_nodes.Robinson.Nodes.BaseNode import RobinsonPyFlowBase
from robinson_flow.ryven_nodes.nodes.components import PrintOutputComponent


class TestNode(RobinsonPyFlowBase):

    def __init__(self, name, uid=None):
        super().__init__(name, cls=PrintOutputComponent, uid=uid)

class OutputNameComponent(OutputPortComponent):

    def __init__(self, name: str):
        super().__init__(name)

    def update(self):
        self.dataport_output(self.name)

class AddHelloComponent(Component):

    msg = None

    dataport_output = DataPortOutput("out")

    def __init__(self, name):
        super().__init__(name)
        self.fstring = "Hello {msg}"

    def dataport_input(self, msg):
        self.msg = msg

    def init(self, fstring:str=None):
        if fstring is not None:
            self.fstring = fstring

    def update(self):
        if self.msg is not None:
            msg = self.fstring.format(**self.__dict__)
            self.dataport_output(msg)
            self.msg = None
            # self.dataport_output(k))
