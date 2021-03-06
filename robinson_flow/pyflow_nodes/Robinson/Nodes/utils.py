from datetime import datetime
from PyFlow.Core.Common import DEFAULT_OUT_EXEC_NAME, PinOptions
from PyFlow.Core.NodeBase import NodeBase
from pydantic.main import BaseModel

from Qt.QtCore import QObject
from Qt.QtWidgets import *
from Qt.QtGui import QImage, QPixmap, QFont
from Qt.QtWidgets import *
from typing import Callable, Type, Any, List, Union
import numpy
import numpy as np
import pandas
import pandas as pd
import pydantic
from robinson.components import Component, DataPortOutput, InputOutputPortComponent
from robinson.components.qt import RobinsonQtComponent

from robinson_flow.logger import getNodeLogger
from typing import Dict

import matplotlib
matplotlib.use('Qt5Agg')

# from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#QTAgg
from matplotlib.figure import Figure
# import inspect
# print(inspect.getmro(FigureCanvas))
# print()


class TickCounter(Component):

    def __init__(self, name: str, fqn_logger=True):
        super().__init__(name, fqn_logger)

        self.last_msg_tick = []
        self.last_update_tick = []

        self.dataport_output_msg_tick_last = DataPortOutput("msg_tick_last")
        self.dataport_output_msg_tick_freq = DataPortOutput("msg_tick_freq")

        self.dataport_output_update_tick_last = DataPortOutput("update_tick_last")
        self.dataport_output_update_tick_freq = DataPortOutput("update_tick_freq")

    def dataport_input(self, msg):
        self.last_msg_tick.append(datetime.now())

        if len(self.last_msg_tick) > 10:
            self.last_msg_tick = self.last_msg_tick[-10:]

    def update(self):

        self.last_update_tick.append(datetime.now())

        if len(self.last_update_tick) > 10:
            self.last_update_tick = self.last_msg_tick[-10:]

        if len(self.last_update_tick) > 2:
            try:
                self.dataport_output_update_tick_last(self.last_update_tick[-1])
                update_tick_freq = (self.last_update_tick[-1] - self.last_update_tick[0]) / len(self.last_update_tick)
                self.dataport_output_update_tick_freq(1/update_tick_freq.total_seconds())
            except Exception as e:
                print(e)

        if len(self.last_msg_tick) > 1:
            msg_tick_dt_max = (self.last_msg_tick[-1] - self.last_msg_tick[0])
            msg_tick_dt = msg_tick_dt_max / len(self.last_msg_tick)
            msg_tick_freq = 1/msg_tick_dt_max.total_seconds()
            self.dataport_output_msg_tick_last(self.last_msg_tick[-1])
            self.dataport_output_msg_tick_freq(msg_tick_freq)
        else:
            self.dataport_output_msg_tick_freq(0)

        # if len(self.last_msg_tick) > 2:
            # self.last_msg_tick = self.last_msg_tick[-2:]

class RandomGenerator(Component):

    def __init__(self, name: str, fqn_logger=True):
        super().__init__(name, fqn_logger)

        self.dataport_output_number = DataPortOutput("number")

    def update(self):
        rnd = numpy.random.random()

        self.dataport_output_number(rnd)

class LoggingView(Component, RobinsonQtComponent):

    def __init__(self, name: str, fqn_logger=True):
        super().__init__(name, fqn_logger)
        self.logger = getNodeLogger(self)

        self.loglines = []

    def init(self):
        self.logwidget = QLabel()
        self.logwidget.resize(30,30)
        # self.logwidget.setLineWrapMode(QPlainTextEdit.NoWrap)
        font = QFont()
        font.setPointSize(6)
        self.logwidget.setFont(font)

    def get_widget(self, parent):
        return self.logwidget


    def dataport_input_msg(self, msg):
        now = datetime.now().strftime("%H:%M:%S")
        msg_line = str(msg)[:250]

        self.loglines.append("{0}: {1}\n".format(now, msg_line))
        log = ""
        for l in self.loglines:
            log+=l

            self.logwidget.setText(log)
            QApplication.processEvents()

            if len(self.loglines) > 50:
                self.loglines = self.loglines[-50:]

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class PlottingView(Component, RobinsonQtComponent):

    class Config(BaseModel):
        max_samples = 100

    def __init__(self, name: str, fqn_logger=True):
        super().__init__(name, fqn_logger)
        self.logger = getNodeLogger(self)

        self.config = PlottingView.Config()

        self.channel_1 = []
        self.channel_2 = []
        self.channel_3 = []
        self.dirty = False

    def init(self):
        pass

    def get_widget(self, parent):

        self.widget = QWidget()
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.sc)

        self.widget.setLayout(self.layout)
        return self.widget

    def config_update(self, max_samples, **kwargs):
        self.config.max_samples = max_samples
        self.reinit = True

    def config_keys(self) -> List[str]:
        return self.config.dict().keys()

    def config_get(self, key=None) -> Dict[str, Any]:
        if key is None:
            return self.config.dict()
        return self.config.dict()[key]

    def update(self):

        if self.dirty:
            self.sc.axes.cla()
            self.sc.axes.plot(self.channel_1, label="channel_1")
            self.sc.axes.plot(self.channel_2, label="channel_2")
            self.sc.axes.plot(self.channel_3, label="channel_3")
            self.sc.axes.legend(loc=3)
            self.sc.draw()

        pass

    def dataport_input_channel_1(self, msg):
        self.channel_1.append(msg)

        if len(self.channel_1) > self.config.max_samples:
            self.channel_1 = self.channel_1[-self.config.max_samples:]

        self.dirty = True

    def dataport_input_channel_2(self, msg):
        self.channel_2.append(msg)
        if len(self.channel_2) > self.config.max_samples:
            self.channel_2 = self.channel_2[-self.config.max_samples:]
        self.dirty = True

    def dataport_input_channel_3(self, msg):
        self.channel_3.append(msg)
        if len(self.channel_3) > self.config.max_samples:
            self.channel_3 = self.channel_3[-self.config.max_samples:]
        self.dirty = True

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

    # code_changed = pyqtSignal(str)
    # code_eval_msg = pyqtSignal(str)
    # code_call_msg = pyqtSignal(str)

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

