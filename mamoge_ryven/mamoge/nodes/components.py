#!/usr/bin/env python3


from vebas.components import Component, DataPortOutput, InputOutputPortComponent, InputPortComponent, OutputPortComponent, Partial
from mamoge_ryven.mamoge.base import MamoGeRyvenWrapper

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
        if self.msg is not None:
            self.logger.info(f"received msg: {self.msg}")
            self.msg = None

class AddComponent(OutputPortComponent):

    a = None
    b = None

    def __init__(self, name: str):
        super().__init__(name)

    def dataport_input_a(self, a):
        self.logger.info(f"input a {a}")
        self.a = a

    def dataport_input_b(self, b):
        self.logger.info(f"input b {b}")
        self.b = b

    def update(self):
        self.logger.info(f"call update method {self.a}, {self.b}")
        if self.a is None or self.b is None:
            return

        self.dataport_output(self.a+self.b)

        self.a = None
        self.b = None

def factory(cls):
    name = cls.__name__
    if name.endswith("Component"):
        name = name[:-len("Component")]

    class RyvenTemplateNode(MamoGeRyvenWrapper):
        """Prints your data"""
        title = name
        # we could also skip the constructor here
        def __init__(self, params):
            super().__init__(cls, params)

    cl =  RyvenTemplateNode
    cl.__name__ = name

    return cl

def export_nodes():

    from vebas.tracking.components.cv import CVVideoInput, RGB2HSV_Transform, ColoredCircleDetection, ImageView, DetectionOverlay, CV_HSVMask_View

    component_list = [TestComponent, PrintOutputComponent, AddComponent, RGB2HSV_Transform, DetectionOverlay, ColoredCircleDetection, Partial]

    #TODO import mamoge components for testing
    #TODO Ports?
    #
    return [factory(c) for c in component_list]
