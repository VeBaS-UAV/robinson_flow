from threading import Thread
from typing import Callable
import PyFlow
from PyFlow.Core import NodeBase
from PyFlow.Core.NodeBase import NodePinsSuggestionsHelper
from PyFlow.Core.Common import *
from blinker.base import Signal
import pydantic
from robinson_flow.ryven_nodes.base import RobinsonWrapperMixin
from robinson_flow.ryven_nodes.nodes.components import PrintOutputComponent

from robinson_flow.ryven_nodes.utils import getNodeLogger

from robinson.components import Component, InputOutputPortComponent, OutputPortComponent, DataPortOutput

from functools import partial

import cProfile
import pstats



class RobinsonPyFlowFunc(NodeBase):
    _packageName = "Robinson"

    def __init__(self, name, cb:Callable, uid=None):
        super().__init__(name, uid)
        self.logger = getNodeLogger(self)
        self.cb = cb
        # self.inExec = self.createInputPin(DEFAULT_IN_EXEC_NAME, 'ExecPin', None, self.compute)
        # self.outExec = self.createOutputPin(DEFAULT_OUT_EXEC_NAME, 'ExecPin')

        input_parameters = inspect.signature(self.cb).parameters

        if input_parameters is not None:

            inp_parameter =  [name for (name, p) in input_parameters.items()]
            print("input pa", inp_parameter)
            for name in input_parameters:
                inp = self.createInputPin(name, "AnyPin",None)
                inp.enableOptions(PinOptions.AllowAny)
                inp.disableOptions(PinOptions.AlwaysPushDirty)
                inp.disableOptions(PinOptions.ChangeTypeOnConnection)
                inp.dirty = False
                inp.dataBeenSet.connect(self.compute)

        self.outp = self.createOutputPin("out", "AnyPin", None)
        self.outp.enableOptions(PinOptions.AllowAny)
        self.outp.disableOptions(PinOptions.ChangeTypeOnConnection)

    def compute(self, *args, **kwargs):

        if self.isDirty():
            try:
                args = [d.getData() for d in self.inputs.values()]

                ret = self.cb(*args)

                self.outp.setData(ret)
            except Exception as e:
                self.logger.warn("Could call function succefully")
                self.logger.error(e)

class RobinsonTicker(NodeBase):
    _packageName = "Robinson"

    def __init__(self, name, uid=None):
        super().__init__(name, uid)
        self.logger = getNodeLogger(self)
        # self.inExec = self.createInputPin(DEFAULT_IN_EXEC_NAME, 'ExecPin', None, self.compute)
        self.outExec = self.createOutputPin(DEFAULT_OUT_EXEC_NAME, 'ExecPin')

        self.thread = None
        self.running = False

        self.profile = cProfile.Profile()
        self.outp = self.createOutputPin("stats", "AnyPin", None)
        self.outp.enableOptions(PinOptions.AllowAny)
        self.outp.disableOptions(PinOptions.ChangeTypeOnConnection)

    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def stop(self):
        self.running = False

        stats = pstats.Stats(self.profile)

        stats.dump_stats("profile.dump")

        self.outp.setData(stats)

    def start(self):
        # if self.thread is not None:
        #     self.running=False
        #     try:
        #         self.thread.join()
        #     except Exception as e:
        #         self.logger.warn(e)

        # self.thread = Thread(target=self.run)
        # self.thread.start()
        self.running = True

    def Tick(self, delta):
        super(RobinsonTicker, self).Tick(delta)
        bEnabled = self.running
        if bEnabled:
            self.profile.enable()
            self.outExec.call()
            self.profile.disable()

    # def run(self):
    #     self.running = True

    #     self.logger.info("Running...")
    #     while self.running:
    #         self.outExec.call()
    #         time.sleep(0.02)
    #     self.logger.info("Stop running")

    @staticmethod
    def category():
        return "utils"

class RobinsonPyFlowBase(NodeBase, RobinsonWrapperMixin):

    _packageName = "Robinson"

    def __init__(self, name, cls, uid=None):
        super().__init__(name, uid=uid)
        self.logger = getNodeLogger(self)
        self.cls = cls

        self.config_args = {}
        self.init_args = {}

        try:
            self.create_component()
            self.create_ports()
        except Exception as e:
            self.logger.error(e)

        self.skip_first_update = True

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
            inp.disableOptions(PinOptions.AlwaysPushDirty)
            inp.disableOptions(PinOptions.ChangeTypeOnConnection)
            inp.dirty = False
            # sig = inspect.signature(port_callable)
            # print("input infos", port_callable, sig)
            self.input_pins[port_name] = (inp, port_callable)


        for port_name, port_callable in output_ports:
            short_name = self.extract_output_name(port_name)
            outp = self.createOutputPin(short_name, "AnyPin", None)
            outp.enableOptions(PinOptions.AllowAny)
            outp.disableOptions(PinOptions.ChangeTypeOnConnection)
            # .disableOptions(PinOptions.AlwaysPushDirty)

            getattr(self.component, port_name).connect(outp.setData)

            self.output_pins[port_name] = (outp, port_callable)


        # create init port
        # create init port
        # init_parameters = self.extract_init_items(self.cls)

        # # print("init parameters", init_parameters)
        # for parameter_name, parameter_type in init_parameters:
        #     # print("init input", parameter_name, parameter_type)
        #     pin_type =self.map_type_to_port(parameter_type)

        #     inp = self.createInputPin(f"init_{parameter_name}", pin_type,None)
        #     inp.enableOptions(PinOptions.AllowAny)
        #     inp.disableOptions(PinOptions.AlwaysPushDirty)
        #     # inp.enableOptions(PinOptions.Dynamic)
        #     # inp.enableOptions(PinOptions.Storable)
        #     inp.dirty = False
        #     self.input_pins[parameter_name] = (inp, partial(self.update_init, parameter_name))


        # # config

        # config_parameters = self.extract_config_items(self.cls)

        # print("Config parameters", config_parameters)
        # for parameter_name,parameter_type in config_parameters:
        #     print("Config input", parameter_name, parameter_type)
        #     pin_type =self.map_type_to_port(parameter_type)
        #     inp = self.createInputPin(f"config_{parameter_name}", pin_type,None)
        #     inp.enableOptions(PinOptions.AllowAny)
        #     inp.disableOptions(PinOptions.AlwaysPushDirty)
        #     inp.dirty = False
        #     self.input_pins[parameter_name] = (inp, partial(self.update_config, parameter_name))


        self.skip_first_update = True

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

        # init_parameters = self.extract_init_items(self.cls)
        # config_parameters = self.extract_config_items(self.cls)

        try:
            if self.isDirty():

                for input_name in self.input_pins:
                    # self.logger.info(f"update port {input_name}")
                    inp, inp_callable = self.input_pins[input_name]
                    if inp.dirty == False:
                        continue

                    if self.skip_first_update:
                        inp.setClean()
                        continue
                    data = inp.getData()
                    # if data is None:
                    if data is None:
                        continue

                    if isinstance(data, str):
                        pass
                    # sig = inspect.signature(inp_callable)
                    # print(sig)
                    if type(data).__name__ == "MyImage":
                        data = data.image

                    # self.logger.info(f"Got input data for port {input_name} {data}")
                    # print(data)

                    inp_callable(data)
                    inp.setClean()
                    # print("####")
                self.skip_first_update = False
        except Exception as e:
            self.logger.warn("Could not get all input data")
            self.logger.error(e)


        # self.logger.info(f"calling update on component")
        self.component.update()


        self.outExec.call()

    def serialize(self):
        data =  super().serialize()

        rob = {}
        rob["input_names"] = list(self.input_pins.keys())
        rob["output_names"] = list(self.output_pins.keys())
        rob["class"] = self.cls.__name__
        rob["module"] = self.cls.__module__

        data["robinson"] = rob

        return data

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
        return "default"

    @staticmethod
    def keywords():
        return []

    @staticmethod
    def description():
        return "Description in rst format."



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
        self.fstring = f"Hello {self.msg}"

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
