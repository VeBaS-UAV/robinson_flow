from PyFlow.Core.Common import DEFAULT_OUT_EXEC_NAME, PinOptions
from PyFlow.Core.NodeBase import NodeBase

from PyQt5.QtCore import pyqtSignal, QObject

import numpy
import numpy as np
import pandas
import pandas as pd

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
        self.inp.dataBeenSet.connect(self.img_received_callback)

    def img_received_callback(self, msg):
        self.msg_received.emit(self.inp.getData())

    @staticmethod
    def category():
        return "utils"

class LambdaNode(NodeBase, QObject):

    _packageName = "Robinson"

    lambda_changed = pyqtSignal(str)
    lambda_eval_msg = pyqtSignal(str)
    lambda_call_msg = pyqtSignal(str)

    def __init__(self, name, uid=None):
        super().__init__(name, uid)
        self.logger = getNodeLogger(self)

        self.inp = self.createInputPin("m", "AnyPin", None)
        self.inp.enableOptions(PinOptions.AllowAny)
        self.inp.disableOptions(PinOptions.ChangeTypeOnConnection)
        self.inp.dataBeenSet.connect(self.call_lambda)

        self.outp = self.createOutputPin("out", "AnyPin", None)
        self.outp.disableOptions(PinOptions.ChangeTypeOnConnection)

        self.lambda_code = "lambda m:m"
        self.lambda_func = lambda m:m

        self.update_lambda(self.lambda_code)

    def update_lambda(self, code):
        if self.lambda_code == code:
            return


        self.lambda_code = code
        try:
            self.lambda_func = eval(self.lambda_code)
        except Exception as e:
            self.lambda_eval_msg.emit(str(e))
            raise e
        self.lambda_changed.emit(self.lambda_code)

    def call_lambda(self, *args):
        try:
            if self.lambda_func is None:
                self.logger.warn(f"Could not find lambda function")
                return

            args = [d.getData() for d in self.inputs.values()]

            ret = self.lambda_func(*args)

            self.outp.setData(ret)
        except Exception as e:
            self.logger.warn("Could not call lambda function")
            self.logger.error(e)
            self.lambda_call_msg.emit(str(e))

    def serialize(self):
        data =  super().serialize()
        data["lambda_code"] = self.lambda_code
        # self.logger.info(f"serialize {data}")
        return data

    def postCreate(self, jsonTemplate=None):
        super().postCreate(jsonTemplate)

        if "lambda_code" in jsonTemplate:
            self.update_lambda(jsonTemplate["lambda_code"])


    @staticmethod
    def category():
        return "utils"

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
