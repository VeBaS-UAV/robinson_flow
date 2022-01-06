#!/usr/bin/env python3


from vebas.components import Component, DataPortOutput, InputOutputPortComponent
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
        if self.msg:
            self.logger.info(f"received msg: {self.msg}")
            self.msg = None


# class TestNode(MamoGeRyvenWrapper):
#     """Prints your data"""
#     title = "Test"
#     # we could also skip the constructor here
#     def __init__(self, params):
#         super().__init__(TestComponent, params)

# class PrintNode(MamoGeRyvenWrapper):
#     """Prints your data"""
#     title = "Print"
#     # we could also skip the constructor here
#     def __init__(self, params):
#         super().__init__(PrintOutputComponent, params)

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

    return RyvenTemplateNode

def export_nodes():
    component_list = [TestComponent, PrintOutputComponent]

    return [factory(c) for c in component_list]
