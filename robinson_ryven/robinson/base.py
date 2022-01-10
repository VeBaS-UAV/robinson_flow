#!/usr/bin/env python3

#import  ryvencore as rc
import ryvencore_qt as rc
from functools import partial
# from robinson_ryven import robinson

from robinson.components import Component
import robinson_ryven.robinson.utils
import robinson_ryven

import inspect

from PyQt5.QtCore import pyqtSignal

class RobinsonRyvenNode(rc.Node):

    def __init__(self, params):
        super().__init__(params)

    @property
    def name(self):
        return self.display_title

class RobinsonRyvenWrapper(RobinsonRyvenNode):

    input_name = "dataport_input"
    output_name = "dataport_output"

    reinit_node = pyqtSignal(RobinsonRyvenNode)

    def __init__(self, cls, params):
        super().__init__(params)
        self.logger = robinson_ryven.robinson.utils.getLogger(self, self.display_title)
        self.logger.info(f"__init__ RyvenWrapper {self.name} with params {params}")
        self.cls = cls
        self.component:Component = None

        self.input_wires = []
        self.output_wires = []

        self.create_component()

    def create_component(self):
        self.logger.info(f"creating component {self.name}")
        self.logger = robinson_ryven.robinson.utils.getLogger(self, self.name)

        try:
                self.component = self.cls(self.title)
        except Exception as e:
                self.logger.error(f"error while setting up component {self.cls}")
                self.logger.error(e)
                self.component = None


    def __del__(self):
        self.logger.warn("DEL CALLED")

    def call_input_port_by_name(self, name, *args, **kw_args):
        # print("call_input_port_by_name", name, args, kw_args)
        func = getattr(self.component, name)

        if name == "dataport_input_marker":
            pass

        if name == "dataport_input_args":
            pass
        try:
            sig = inspect.signature(func)
            param = sig.parameters
            # print("sig", sig, param, param.items())
            if len(param.items()) == 0:
                func()
            if len(param.items()) == 1:
                func(*args, **kw_args)
            elif len(param.items()) > 1:
                if len(args) > 1:
                    func(*args, **kw_args)
                else:
                    if isinstance(args[0], set):
                        func(*args[0])
                    elif isinstance(args[0], tuple):
                        func(*args[0])
                    elif isinstance(args[0], dict):
                        func(**args[0])
        except Exception as e:
            self.logger.error(f"Could not call input porty {self.cls}.{name}")
            self.logger.error(e)

    def call_output_port_by_index(self, index, *args, **kw_args):
        # print("call outputport by index", index, args, kw_args)
        if len(args) == 1:
            self.outputs[index].set_val(args[0])
        else:
            self.outputs[index].set_val(args)

    def cl_input_ports(self, cl):
        ports = [f for f in dir(cl) if f.startswith(self.input_name)]
        return ports

    def cl_output_ports(self, cl):
        return [f for f in dir(cl) if f.startswith(self.output_name)]

    def extract_output_name(self, port_name):
        base_name = port_name[len(self.output_name)+1:]
        if len(base_name) == 0:
            return "output"
        return base_name

    def extract_input_name(self, port_name):
        base_name = port_name[len(self.input_name)+1:]
        if len(base_name) == 0:
            return "input"
        return base_name

    def setup_ports(self, inputs_data=None, outputs_data=None):
        # overwrite default port creation

        if self.component is None:
            self.logger.warn("No component available for {self.cls}, could not init ports")
            return

        try:
            print("setup ports")
            input_ports = self.cl_input_ports(self.component)
            output_ports = self.cl_output_ports(self.component)

            for port_name in input_ports:
                port_index = len(self.inputs)
                self.create_input(self.extract_input_name(port_name))
                # self.create_input(port_name[port_name.rfind("_")+1:])
                # print("creating input port at index ", port_index)
                self.input_wires.append(partial(self.call_input_port_by_name, port_name))

            for output_port in output_ports:
                port_index = len(self.outputs)
                # print("create output wirde for index", port_index, output_port)
                self.create_output(self.extract_output_name(output_port))
                # self.create_output(output_port[output_port.rfind("_")+1:])
                # getattr(self.component, output_port).connect(lambda *args, **kw_args: self.outputs[port_index].set_val(*args, **kw_args))
                # getattr(self.component, output_port).connect(lambda *args, **kw_args: self.outputs[port_index].set_val(args[0]))
                getattr(self.component, output_port).connect(partial(self.call_output_port_by_index, port_index))
        except Exception as e:
            self.logger.error(f"Error while setting up ports for {self.component}")
            self.logger.error(e)

    def update_event(self, inp=-1):
        self.logger.info(f"update_event for node {self.name}, {inp}")
        if inp > -1:
            self.logger.info(f"update input wires")
            self.input_wires[inp](self.input(inp))
        else:
            self.logger.info(f"call super().update_event(inp)")
            super().update_event(inp)

        try:
            self.component.update()
        except Exception as e:
            self.logger.warn("Error occured in update_event")
            self.logger.warn(e)


    def init(self,**kwargs):
        self.logger.info(f"init with args {kwargs}")
        self.component.init(**kwargs)

    def set_state(self, data: dict, version):
        self.logger.info(f"set_state of base {data}")
        return super().set_state(data, version)


    def change_title(self):
        self.logger.info(f"change_title")
        old_title = self.name
        super().change_title()

        self.logger.info(f"title {old_title} vs {self.name}")
        if old_title != self.name:
            self.reinit_node.emit(self)
            pass

    def set_display_title(self, t: str):
        super().set_display_title(t)
        self.reinit_node.emit(self)
