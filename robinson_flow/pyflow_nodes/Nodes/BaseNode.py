import PyFlow
from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *
import pydantic
from robinson_ryven.ryven_nodes.base import RobinsonWrapperMixin
from robinson_ryven.ryven_nodes.nodes.components import PrintOutputComponent

from robinson_ryven.ryven_nodes.utils import getNodeLogger

from robinson.components import Component, InputOutputPortComponent

from functools import partial


class RobinsonPyFlowBase(NodeBase, RobinsonWrapperMixin):

    _packageName = "robinson"

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

            # sig = inspect.signature(port_callable)
            # print("input infos", port_callable, sig)
            self.input_pins[short_name] = (inp, port_callable)


        for port_name, port_callable in output_ports:
            short_name = self.extract_output_name(port_name)
            outp = self.createOutputPin(short_name, "AnyPin", None)
            outp.enableOptions(PinOptions.AllowAny)

            getattr(self.component, port_name).connect(outp.setData)

            self.output_pins[short_name] = (outp, port_callable)


        # create init port
        # create init port
        init_parameters = self.extract_init_items(self.cls)

        print("init parameters", init_parameters)
        for parameter_name, parameter_type in init_parameters:
            print("init input", parameter_name, parameter_type)
            pin_type =self.map_type_to_port(parameter_type)

            inp = self.createInputPin(f"init_{parameter_name}", pin_type,None)
            inp.enableOptions(PinOptions.AllowAny)
            self.input_pins[parameter_name] = (inp, partial(self.update_init, parameter_name))


        # config

        config_parameters = self.extract_config_items(self.cls)

        print("Config parameters", config_parameters)
        for parameter_name,parameter_type in config_parameters:
            print("Config input", parameter_name, parameter_type)
            pin_type =self.map_type_to_port(parameter_type)
            inp = self.createInputPin(f"config_{parameter_name}", pin_type,None)
            inp.enableOptions(PinOptions.AllowAny)
            self.input_pins[parameter_name] = (inp, partial(self.update_init, parameter_name))


    def map_type_to_port(self, typeclass):
        port_type_mapping = {}
        port_type_mapping[str] = "StringPin"
        port_type_mapping[int] = "IntPin"
        port_type_mapping[float] = "FloatPin"
        port_type_mapping[bool] = "BoolPin"
        port_type_mapping[None] = "AnyPin"

        if typeclass in port_type_mapping:
            return port_type_mapping[typeclass]

        return "AnyPin"

    def compute(self, *args, **kwargs):
        # print("compute")
        # self.port_callback(self.inp.getData())

        init_parameters = self.extract_init_items(self.cls)
        config_parameters = self.extract_config_items(self.cls)

        try:
            if self.isDirty() == False:
                return

            for input_name in self.input_pins:
                # self.logger.info(f"update port {input_name}")
                inp, inp_callable = self.input_pins[input_name]
                data = inp.getData()
                # if data is None:
                # sig = inspect.signature(inp_callable)
                # print(sig)
                if type(data).__name__ == "MyImage":
                    data = data.image

                self.logger.info(f"Got input data for port {input_name} {data}")
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



class AddHelloComponent(InputOutputPortComponent):

    msg = None

    def __init__(self, name):
        super().__init__(name)
        self.fstring = f"Hello {self.msg}"

    def dataport_input(self, msg):

        self.msg = msg

    def init(self, fstring:str):
        self.fstring = fstring

    def update(self):
        if self.msg is not None:
            self.dataport_output(self.fstring)
