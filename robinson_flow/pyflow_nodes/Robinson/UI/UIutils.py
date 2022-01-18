
from PyFlow.UI.Canvas.UINodeBase import UINodeBase
from PyFlow.UI.Widgets.SelectPinDialog import SelectPinDialog
# from PyFlow.Core.ExternalManager import ExternalManagerSingleton
from PyFlow.UI.Utils.stylesheet import Colors
from PyFlow.UI import RESOURCES_DIR
from PyFlow.UI.Canvas.UICommon import *
from vebas.tracking.components.cv import ImageView
from Qt.QtWidgets import QTextEdit, QLineEdit, QLabel, QPlainTextEdit, QTextEdit
from Qt.QtGui import QImage, QPixmap, QFont
from Qt.QtCore import Qt
from robinson_flow.pyflow_nodes.Robinson.Nodes.ExternalNodes import ExternalSource
from robinson_flow.pyflow_nodes.Robinson.Nodes.OpenCV import FrameView
import cv2

from robinson_flow.pyflow_nodes.Robinson.Nodes.utils import LambdaNode, LoggingView

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
