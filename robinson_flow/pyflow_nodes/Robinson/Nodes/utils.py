from PyFlow.Core.Common import DEFAULT_OUT_EXEC_NAME, PinOptions
from PyFlow.Core.NodeBase import NodeBase

from PyQt5.QtCore import pyqtSignal, QObject

from typing import Callable, Type, Any, List, Union
import numpy
import numpy as np
import pandas
import pandas as pd
import pydantic
from robinson.components import Component, InputOutputPortComponent

from robinson_flow.logger import getNodeLogger

class OnMessageExec(NodeBase, QObject):

    _packageName = "Robinson"

    def __init__(self, name, uid=None):
        super().__init__(name, uid)
        self.logger = getNodeLogger(self)

        self.msg_received = False
        self.outExec = self.createOutputPin(DEFAULT_OUT_EXEC_NAME, 'ExecPin')

        self.inp = self.createInputPin("msg", "AnyPin", None)
        self.inp.enableOptions(PinOptions.AllowAny)
        self.inp.dataBeenSet.connect(self.msg_callback)

    def msg_callback(self, msg):
        self.msg_received = True

    def Tick(self, delta):
        if self.msg_received:
            self.outExec.call()
            self.msg_received = False

    @staticmethod
    def category():
        return "utils"

class LoggingView(NodeBase, QObject):

    _packageName = "Robinson"
    connections:dict = {}

    msg_received = pyqtSignal(object)

    def __init__(self, name, uid=None):
        super().__init__(name, uid)
        self.logger = getNodeLogger(self)

        self.inp = self.createInputPin("msg", "AnyPin", None)
        self.inp.enableOptions(PinOptions.AllowAny)
        self.inp.enableOptions(PinOptions.AllowMultipleConnections)
        self.inp.dataBeenSet.connect(self.img_received_callback)

    def img_received_callback(self, msg):
        self.msg_received.emit(self.inp.getData())

    @staticmethod
    def category():
        return "utils"

class LambdaComponent(InputOutputPortComponent):

    class Config(pydantic.BaseModel):
        lambda_code:str = "lambda m:m"

    config = Config()

    def __init__(self, name):
        super().__init__(name)
        self.msg = None

        self.update_lambda()

    def config_update(self, **kwargs):
        self.config = LambdaComponent.Config(**kwargs)
        self.update_lambda()

    def config_get(self, key=None) -> dict[str, Any]:
        if key is None:
            return self.config.dict()
        return self.config["key"]

    def update_lambda(self):
        try:
            self.lambda_func = eval(self.config.lambda_code)
        except Exception as e:
            self.logger.warn(f"Could not eval code {self.config.lambda_code}")

    def dataport_input(self, msg):
        self.msg = msg

    def update(self):
        if self.msg:

            try:
                if self.lambda_func is None:
                    self.logger.warn(f"Could not find lambda function")
                    return

                args = [self.msg]
                ret = self.lambda_func(*args)

                self.dataport_output(ret)
            except Exception as e:
                self.logger.warn("Could not call lambda function")
                self.logger.error(e)

            self.msg = None


class EvalNode(NodeBase, QObject):

    _packageName = "Robinson"

    code_changed = pyqtSignal(str)
    code_eval_msg = pyqtSignal(str)
    code_call_msg = pyqtSignal(str)

    def __init__(self, name, uid=None):
        super().__init__(name, uid)
        self.logger = getNodeLogger(self)

        self.outp = self.createOutputPin("out", "AnyPin", None)
        self.outp.disableOptions(PinOptions.ChangeTypeOnConnection)

        self.code = ""

        self.update_code(self.code)

    def update_code(self, code):
        if self.code == code:
            return

        self.code = code
        try:
            self.result = eval(self.code)
            self.outp.setData(self.result)
        except Exception as e:
            self.code_eval_msg.emit(str(e))
            raise e
        self.code_changed.emit(self.code)

    def serialize(self):
        data =  super().serialize()
        data["code"] = self.code
        # self.logger.info(f"serialize {data}")
        return data

    def postCreate(self, jsonTemplate=None):
        super().postCreate(jsonTemplate)

        if "code" in jsonTemplate:
            self.update_code(jsonTemplate["code"])


    @staticmethod
    def category():
        return "utils"

class PlotView(NodeBase, QObject):

    _packageName = "Robinson"
    connections:dict = {}

    msg_received = pyqtSignal(object)

    def __init__(self, name, uid=None):
        super().__init__(name, uid)
        self.logger = getNodeLogger(self)

        self.inp = self.createInputPin("msg", "AnyPin", None)
        self.inp.enableOptions(PinOptions.AllowAny)
        self.inp.dataBeenSet.connect(self.img_received_callback)

    def img_received_callback(self, msg):
        self.msg_received.emit(self.inp.getData())

    @staticmethod
    def category():
        return "utils"
