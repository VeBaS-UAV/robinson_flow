from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *
from robinson_ryven.robinson.base import RobinsonWrapperMixin
from robinson_ryven.robinson.nodes.components import PrintOutputComponent

from robinson_ryven.robinson.utils import getNodeLogger

from robinson.components import Component

from functools import partial

class RobinsonPyFlowBase(NodeBase, RobinsonWrapperMixin):

    def __init__(self, name, cls, uid=None):
        super().__init__(name, uid=uid)
        self.logger = getNodeLogger(self)
        self.cls = cls

        try:
            self.create_component()
            self.create_ports()
        except Exception as e:
            self.logger.error(e)

    def create_ports(self):
        self.inExec = self.createInputPin(DEFAULT_IN_EXEC_NAME, 'ExecPin', None, self.compute)
        self.outExec = self.createOutputPin(DEFAULT_OUT_EXEC_NAME, 'ExecPin')

        input_ports = self.cl_input_ports(self.component)
        output_ports = self.cl_output_ports(self.component)

        self.input_pins = {}
        self.output_pins = {}
        for port_name, port_callable in input_ports:
            short_name = self.extract_input_name(port_name)
            inp = self.createInputPin(short_name, "AnyPin",None)
            inp.enableOptions(PinOptions.AllowAny)

            sig = inspect.signature(port_callable)
            print("input infos", port_callable, sig)
            self.input_pins[short_name] = (inp, port_callable)


        for port_name, port_callable in output_ports:
            short_name = self.extract_output_name(port_name)
            outp = self.createOutputPin(short_name, "AnyPin", None)
            outp.enableOptions(PinOptions.AllowAny)

            getattr(self.component, port_name).connect(outp.setData)

            self.output_pins[short_name] = (outp, port_callable)

    def port_callback(self, *args, **kwargs):
        self.logger.info(f"port_callback {args}, {kwargs}")

    def compute(self, *args, **kwargs):
        # print("compute")
        # self.port_callback(self.inp.getData())

        try:
            for input_name in self.input_pins:
                # self.logger.info(f"update port {input_name}")
                inp, inp_callable = self.input_pins[input_name]
                data = inp.getData()
                # if data is None:
                # sig = inspect.signature(inp_callable)
                # print(sig)
                # print(data)
                inp_callable(data)
                # print("####")
        except Exception as e:
            self.logger.warn("Could not get all input data")
            self.logger.error(e)

        # self.logger.info(f"calling update on component")
        self.component.update()


        self.outExec.call()
    
    @staticmethod
    def pinTypeHints():
        helper = NodePinsSuggestionsHelper()
        helper.addInputDataType('BoolPin')
        helper.addOutputDataType('BoolPin')
        helper.addInputStruct(StructureType.Single)
        helper.addOutputStruct(StructureType.Single)
        return helper

    @staticmethod
    def category():
        return 'test'

    @staticmethod
    def keywords():
        return []

    @staticmethod
    def description():
        return "Description in rst format."

class TestNode(RobinsonPyFlowBase):

    def __init__(self, name, uid=None):
        super().__init__(name, cls=PrintOutputComponent, uid=uid)

