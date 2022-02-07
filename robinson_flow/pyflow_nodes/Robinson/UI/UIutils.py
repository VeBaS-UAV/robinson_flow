
from PyFlow.UI.Canvas.UINodeBase import UINodeBase
from PyFlow.UI.Widgets.SelectPinDialog import SelectPinDialog
# from PyFlow.Core.ExternalManager import ExternalManagerSingleton
from PyFlow.UI.Utils.stylesheet import Colors
from PyFlow.UI import RESOURCES_DIR
from PyFlow.UI.Canvas.UICommon import *
from vebas.tracking.components.cv import ImageView
from Qt.QtWidgets import QTextEdit, QLineEdit, QLabel, QPlainTextEdit, QTextEdit, QPushButton
from Qt.QtGui import QImage, QPixmap, QFont
from Qt.QtCore import Qt
from robinson_flow.pyflow_nodes.Robinson.Nodes.BaseNode import RobinsonProfiler
from robinson_flow.pyflow_nodes.Robinson.Nodes.ExternalNodes import ExternalSource
from robinson_flow.pyflow_nodes.Robinson.Nodes.OpenCV import FrameView
import cv2

from robinson_flow.pyflow_nodes.Robinson.Nodes.utils import EvalNode, LambdaNode, LoggingView, PlotView

import datetime

class UILoggingView(UINodeBase):
#     pinCreated = QtCore.Signal(object)

    def __init__(self, raw_node):
        super(UILoggingView, self).__init__(raw_node)
        self.node:LoggingView = raw_node
        self.node.msg_received.connect(self.msg_updated)
        self.resizable = True

        self.logwidget = QLabel()
        self.logwidget.resize(30,30)
        # self.logwidget.setLineWrapMode(QPlainTextEdit.NoWrap)
        font = QFont()
        font.setPointSize(6)
        self.logwidget.setFont(font)

        self.addWidget(self.logwidget)

        self.loglines = []

    def msg_updated(self, msg):
        try:
            # horScrollBar = self.logwidget.horizontalScrollBar()
            # verScrollBar = self.logwidget.verticalScrollBar()
            # scrollIsAtEnd = verScrollBar.maximum() - verScrollBar.value() <= 10

            now = datetime.datetime.now().strftime("%H:%M:%S")
            msg_line = str(msg)[:70]

            self.loglines.append("{0}: {1}\n".format(now, msg_line))
            log = ""
            for l in self.loglines:
                log+=l

            self.logwidget.setText(log)

            if len(self.loglines) > 5:
                self.loglines = self.loglines[-5:]
            # if scrollIsAtEnd:
                # verScrollBar.setValue(verScrollBar.maximum()) # Scrolls to the bottom
                # horScrollBar.setValue(0) # scroll to the left
        except Exception as e:
            print(e)
class UIEvalView(UINodeBase):
#     pinCreated = QtCore.Signal(object)

    def __init__(self, raw_node):
        super(UIEvalView, self).__init__(raw_node)
        self.node:EvalNode = raw_node
        self.node.code_changed.connect(self.code_changed)
        self.node.code_eval_msg.connect(self.code_eval_msg)
        self.node.code_call_msg.connect(self.code_call_msg)
        self.resizable = True

        self.codewidget = QPlainTextEdit()
        self.codewidget.setPlainText(self.node.code)
        self.codewidget.resize(90,100)
        # self.codewidget.textChanged.connect(self.code_updated)
        # self.codewidget.setLineWrapMode(QPlainTextEdit.NoWrap)
        font = QFont()
        font.setPointSize(8)
        self.codewidget.setFont(font)

        self.addWidget(self.codewidget)

        self.eval_button = QPushButton()
        self.eval_button.setText("eval")
        self.eval_button.clicked.connect(self.code_updated)

        self.eval_msg = QLabel()
        self.eval_msg.setFont(font)
        self.eval_msg.setStyleSheet('color: red')
        self.addWidget(self.eval_button)
        self.addWidget(self.eval_msg)

    def code_eval_msg(self, msg):
        self.eval_msg.setText(msg)

    def code_call_msg(self, msg):
        self.eval_msg.setText(msg)

    def code_changed(self, code):
        self.codewidget.setPlainText(code)

    def code_updated(self):
        try:
            code = self.codewidget.toPlainText()
            self.node.update_code(code)
            self.eval_msg.setText("")
        except Exception as e:
            self.eval_msg.setText(str(e))

class UILambdaView(UINodeBase):
#     pinCreated = QtCore.Signal(object)

    def __init__(self, raw_node):
        super(UILambdaView, self).__init__(raw_node)
        self.node:LambdaNode = raw_node
        self.node.lambda_changed.connect(self.lambda_changed)
        self.node.lambda_eval_msg.connect(self.lambda_eval_msg)
        self.node.lambda_call_msg.connect(self.lambda_call_msg)
        self.resizable = True

        self.lambdawidget = QLineEdit()
        self.lambdawidget.setText(self.node.lambda_code)
        self.lambdawidget.resize(90,20)
        self.lambdawidget.textEdited.connect(self.code_updated)
        # self.lambdawidget.setLineWrapMode(QPlainTextEdit.NoWrap)
        font = QFont()
        font.setPointSize(8)
        self.lambdawidget.setFont(font)

        self.addWidget(self.lambdawidget)


        self.eval_msg = QLabel()
        self.eval_msg.setFont(font)
        self.eval_msg.setStyleSheet('color: red')
        self.addWidget(self.eval_msg)

    def lambda_eval_msg(self, msg):
        self.eval_msg.setText(msg)

    def lambda_call_msg(self, msg):
        self.eval_msg.setText(msg)

    def lambda_changed(self, code):
        self.lambdawidget.setText(code)

    def code_updated(self):
        try:
            code = self.lambdawidget.text()
            self.node.update_lambda(code)
            self.eval_msg.setText("")
        except Exception as e:
            self.eval_msg.setText(str(e))

class UIRobinsonProfilerView(UINodeBase):
#     pinCreated = QtCore.Signal(object)

    def __init__(self, raw_node):
        super(UIRobinsonProfilerView, self).__init__(raw_node)
        self.node:RobinsonProfiler = raw_node
        self.resizable = True

        self.lambdawidget = QPushButton()
        self.lambdawidget.setText("Toggle")
        self.lambdawidget.clicked.connect(self.node.toggle)
        # self.lambdawidget.setLineWrapMode(QPlainTextEdit.NoWrap)

        self.addWidget(self.lambdawidget)

class UIRobinsonTickerView(UINodeBase):
#     pinCreated = QtCore.Signal(object)

    def __init__(self, raw_node):
        super(UIRobinsonTickerView, self).__init__(raw_node)
        self.node:RobinsonProfiler = raw_node
        self.resizable = True

        self.stop = QPushButton()
        self.stop.setText("Stop")
        self.stop.clicked.connect(lambda: self.node.stop())

        self.single_step = QPushButton()
        self.single_step.setText("Step")
        self.single_step.clicked.connect(lambda: self.node.single_step())

        self.play1 = QPushButton()
        self.play1.setText("Play (1)")
        self.play1.clicked.connect(lambda: self.node.start(1))

        self.play10 = QPushButton()
        self.play10.setText("Play (10)")
        self.play10.clicked.connect(lambda: self.node.start(10))

        self.play100 = QPushButton()
        self.play100.setText("Play (100)")
        self.play100.clicked.connect(lambda: self.node.start(100))

        self.addWidget(self.stop)
        self.addWidget(self.single_step)
        self.addWidget(self.play1)
        self.addWidget(self.play10)
        self.addWidget(self.play100)


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class UIRobinsonPlotView(UINodeBase):
#     pinCreated = QtCore.Signal(object)

    def __init__(self, raw_node):
        super(UIRobinsonPlotView, self).__init__(raw_node)
        self.node:PlotView = raw_node
        self.resizable = True

        self.sc = MplCanvas()
        self.sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])
        self.addWidget(self.sc)
