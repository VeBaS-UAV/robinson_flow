from PyFlow.Core.Common import PinOptions
from PyFlow.Core.NodeBase import NodeBase

from robinson_flow.ryven_nodes.utils import getNodeLogger

from PyQt5.QtCore import pyqtSignal, QObject


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
