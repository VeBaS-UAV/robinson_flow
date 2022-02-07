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

from robinson_flow.config import settings



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

        self.dt_exec = 1
        self.last_exec = time.time()
        self.running = False

    def Tick(self, delta):

        if self.running is False:
            return

        if self.dt_exec == 0:
            self.step()
            self.dt_exec = -1
            self.running = False

        if self.dt_exec > 0:
            if time.time() - self.last_exec > self.dt_exec:
                self.step()

    def single_step(self):
        self.running = True
        self.dt_exec = 0

    def step_rate(self, rate):
        self.dt_exec = 1.0/rate

    def stop(self):
        self.running = False

    def start(self, rate=None):
        if rate is not None:
            self.step_rate(rate)
        self.running = True

    def step(self):
        self.outExec.call()
        self.last_exec = time.time()


    @staticmethod
    def category():
        return "utils"

class RobinsonProfiler(NodeBase):

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
        super(RobinsonProfiler, self).Tick(delta)
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


        self.update_settings()

        self.skip_first_update = True

    # def update_settings(self):
    #     if self.component is None:
    #         return

    #     if self.name in settings:

    #         cfg = settings[self.name]
    #         try:
    #             self.component.config_update(**{k:v for (k,v) in cfg.items()})
    #         except Exception as e:
    #             self.logger.error(f"Could not set config for {self.name}")
    #             self.logger.error(e)

    def setName(self, name):
        super().setName(name)
        # self.update_settings()


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

        rob["config"] = self.component.config_get()

        data["robinson"] = rob

        return data

    def postCreate(self, jsonTemplate=None):
        super().postCreate(jsonTemplate)

        if "robinson" in jsonTemplate:
            rob = jsonTemplate["robinson"]
            if "config" in rob:
                    try:
                        self.component.config_update(**rob["config"])
                    except Exception as e:
                        self.logger.error(f"Could not set config for {self.name}")
                        self.logger.error(e)

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

