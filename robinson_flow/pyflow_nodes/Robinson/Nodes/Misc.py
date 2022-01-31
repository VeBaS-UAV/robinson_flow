#!/usr/bin/env python3

from pydantic.main import BaseModel
from robinson.components import Component, DataPortOutput, OutputPortComponent
from robinson_flow import config
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

    class Config(BaseModel):
        fstring:str = "Hello {msg}"


    config = Config()

    msg = None

    dataport_output = DataPortOutput("out")

    def __init__(self, name):
        super().__init__(name)

    def dataport_input(self, msg):
        self.msg = msg

    def update(self):
        if self.msg is not None:
            msg = self.config.fstring.format(**self.__dict__)
            self.dataport_output(msg)
            self.msg = None
            # self.dataport_output(k))

    def config_update(self, **kwargs):
        print("config update")
        self.config = AddHelloComponent.Config(**{**self.config.dict(), **kwargs})
