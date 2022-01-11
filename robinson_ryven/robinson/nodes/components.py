#!/usr/bin/env python3


import inspect
import sys
from socket import MsgFlag
from robinson.components import Component, DataPortOutput, InputOutputPortComponent, OutputPortComponent, Port
from robinson_ryven.robinson.base import RobinsonRyvenWrapper

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
        self.console_output = ""
        self.console_counter = 0

    def dataport_input_msg(self, msg):
        self.msg = msg

    def dataport_input_args(self, *args):
        #self.logger.info(f"received args {args}")
        self.msg = args

    def dataport_input_kwargs(self, **kwargs):
        #self.logger.info(f"received kwargs {kwargs}")
        self.msg = kwargs

    def dataport_input_args_kwargs(self, *args, **kwargs):
        #self.logger.info(f"received args_kwargs {args}, {kwargs}")
        self.msg = args, kwargs

    def dataport_input_multi_args(self, arg1, arg2):
        #self.logger.info(f"received multi args {arg1}, {arg2}")
        self.msg = arg1, arg2

    def init(self, console_output, **kwargs):
        self.logger.info(f"Init called with args {kwargs}")
        self.console_output = console_output

    def config(self, console_counter, **kwargs):
        self.logger.info(f"Config called with args {kwargs}")
        self.console_counter = console_counter


    def update(self):
        if self.msg is not None:
            self.logger.info(f"{self.console_output}: {self.msg} ({self.console_counter})")
            self.console_counter += 1
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

    class RyvenTemplateNode(RobinsonRyvenWrapper):
        """Prints your data"""
        title = name
        base_class = cls
        # we could also skip the constructor here
        def __init__(self, params):
            super().__init__(cls, params)

    cl =  RyvenTemplateNode
    cl.__name__ = name

    return cl

class MyPartial(Port):

    def __init__(self, name):
        super().__init__(name)
        # self.args = [1]
        # self.kw_args = {}

    def __call__(self, *fargs, **fkw_args):
        # return super().__call__(*self.args, *fargs, **{**self.kw_args, **fkw_args})
        return super().__call__(*fargs, **fkw_args)

def load_components_from_module(module):
    results =  []
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            if sys.modules[obj.__module__] == module:
                if issubclass(obj, Component):
                    results.append(obj)
    return results

def export_nodes():

    import vebas.tracking.components.cv #import CVVideoInput, RGB2HSV, BGR2HSV, RGB2BRG, BGR2RGB, ColoredCircleDetection, ImageView, DetectionOverlay, CV_HSVMask_View
    import vebas.tracking.components.control
    import vebas.tracking.components.filter
    import vebas.tracking.components.transform
    import vebas.tracking.kf_ctl_loop.components as kf_ctl

    component_list = []#[TestComponent, PrintOutputComponent, AddComponent, RGB2HSV, BGR2HSV, RGB2BRG, BGR2RGB, DetectionOverlay, ColoredCircleDetection, MyPartial]

    # component_list.extend(load_components_from_module(vebas.tracking.components.cv))
    # component_list.extend(load_components_from_module(vebas.tracking.components.control))
    # component_list.extend(load_components_from_module(vebas.tracking.components.filter))
    # component_list.extend(load_components_from_module(vebas.tracking.components.transform))
    # component_list.extend(load_components_from_module(kf_ctl))


    component_list.append(TestComponent)
    component_list.append(PrintOutputComponent)

    #TODO import robinson components for testing
    #TODO Ports?
    #
    return [factory(c) for c in component_list]
