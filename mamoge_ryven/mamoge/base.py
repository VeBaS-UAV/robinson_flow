#!/usr/bin/env python3


import ryvencore_qt as rc
from functools import partial

class MamoGeRyvenNode(rc.Node):

    def __init__(self, params):
        super().__init__(params)


    # def update(self, inp=-1):
    #     # print("update", inp)
    #     #return super().update(inp=inp)
    #     #do not propagate update, executor will do it
    #     return


class MamoGeRyvenWrapper(MamoGeRyvenNode):

    def __init__(self, component, params):
        super().__init__(params)
        self.component = component(self.title)

        self.input_wires = []
        self.output_wires = []

    def call_input_port_by_name(self, name, *args, **kw_args):
        # print("call_input_port_by_name", name, args, kw_args)
        getattr(self.component, name)(*args, **kw_args)

    def call_output_port_by_index(self, index, *args, **kw_args):
        # print("call outputport by index", index, args, kw_args)
        self.outputs[index].set_val(args[0])

    def cl_input_ports(self, cl):
        return [f for f in cl.__class__.__dict__.keys() if f.startswith("dataport_input")]

    def cl_output_ports(self, cl):
        return [f for f in cl.__dict__.keys() if f.startswith("dataport_output")]

    def setup_ports(self, inputs_data=None, outputs_data=None):
        # overwrite default port creation
        #
        input_ports = self.cl_input_ports(self.component)
        output_ports = self.cl_output_ports(self.component)

        for port_name in input_ports:
            port_index = len(self.inputs)
            self.create_input(port_name[port_name.rfind("_")+1:])
            # print("creating input port at index ", port_index)
            self.input_wires.append(partial(self.call_input_port_by_name, port_name))

        for output_port in output_ports:
            port_index = len(self.outputs)
            # print("create output wirde for index", port_index, output_port)
            self.create_output(output_port[output_port.rfind("_")+1:])
            # getattr(self.component, output_port).connect(lambda *args, **kw_args: self.outputs[port_index].set_val(*args, **kw_args))
            # getattr(self.component, output_port).connect(lambda *args, **kw_args: self.outputs[port_index].set_val(args[0]))
            getattr(self.component, output_port).connect(partial(self.call_output_port_by_index, port_index))

    # def update(self, inp=-1):
    #     # print("update", inp)
    #     # if inp >= 0:
    #         # print("call input wires", inp)
    #         # self.input_wires[inp](self.input(inp))
    #     super().update(inp)
    #     return


    def update_event(self, inp=-1):
        # print("update event")
        self.component.update()
