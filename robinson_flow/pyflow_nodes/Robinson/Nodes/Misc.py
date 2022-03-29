#!/usr/bin/env python3

from pydantic.main import BaseModel
from robinson.components import Component, DataPortOutput, EventPortOutput, OutputPortComponent, InputOutputPortComponent, InputPortComponent
from robinson.components.qt import RobinsonQtComponent

from robinson_flow import config
from robinson_flow.pyflow_nodes.Robinson.Nodes.BaseNode import RobinsonPyFlowBase

from Qt.QtWidgets import *
from Qt import QtGui
from Qt import QtCore

class ConsoleOutputComponent(InputPortComponent):

    def __init__(self, name: str):
        super().__init__(name)

    def dataport_input(self, msg):
        print("dateport input", msg)
        self.logger.info(msg)

class OutputNameComponent(OutputPortComponent):

    def __init__(self, name: str):
        super().__init__(name)

    def update(self):
        self.dataport_output(self.name)

class AddHelloComponent(Component):

    class Config(BaseModel):
        fstring:str = "Hello {msg}"


    def __init__(self, name):
        super().__init__(name)

        self.config = AddHelloComponent.Config()
        self.msg = None
        self.dataport_output = DataPortOutput("out")

    def dataport_input(self, msg):
        self.msg = msg

    def dataport_input_test2(self, msg):
        self.msg = msg

    def dataport_input_test3(self, msg):
        self.msg = msg

    def update(self):
        if self.msg is not None:
            msg = self.config.fstring.format(**self.__dict__)
            # print("dataport_output_hex", hex(id(self)),hex(id(self.dataport_output)))
            self.dataport_output(msg)
            self.msg = None
            # self.dataport_output(k))

    def config_update(self, **kwargs):
        self.config = AddHelloComponent.Config(**{**self.config.dict(), **kwargs})

    def config_get(self, key=None):
        if key is None:
            return self.config.dict()
        return self.config["key"]


class TestEventComponent(Component, RobinsonQtComponent):

    def __init__(self, name: str, fqn_logger=True):
        super().__init__(name, fqn_logger)

        self.dataport_output_onevent = DataPortOutput("eventmsg")
        self.eventport_output_eventforward = EventPortOutput("eventforward")

    def dataport_input_blank(self, msg):
        print("got input", msg)
        pass

    def eventport_input_inputevent(self):
        self.logger.error(f"received event")
        self.dataport_output_onevent("Received event")
        self.eventport_output_eventforward()

    def get_widget(self, parent):
        self.layout = QVBoxLayout()

        self.btn = QPushButton("Klick!")
        self.btn.clicked.connect(lambda:self.dataport_output_onevent("klick"))
        self.btn.clicked.connect(self.eventport_output_eventforward)

        self.layout.addWidget(self.btn)

        self.widget = QWidget()

        self.widget.setLayout(self.layout)

        return self.widget
