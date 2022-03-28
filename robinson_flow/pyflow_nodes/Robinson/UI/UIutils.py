
from PyFlow.UI.Canvas.UINodeBase import UINodeBase
from PyFlow.UI.Widgets.SelectPinDialog import SelectPinDialog
from PyFlow.UI.Utils.stylesheet import Colors
from PyFlow.UI import RESOURCES_DIR
from PyFlow.UI.Canvas.UICommon import *
from vebas.tracking.components.cv import ImageView
from Qt.QtWidgets import QTextEdit, QLineEdit, QLabel, QPlainTextEdit, QTextEdit, QPushButton
from Qt.QtGui import QImage, QPixmap, QFont
from Qt.QtCore import Qt
from robinson_flow.pyflow_nodes.Robinson.Nodes.BaseNode import RobinsonProfiler
from robinson_flow.pyflow_nodes.Robinson.Nodes.ExternalNodes import ExternalSource
from robinson_flow.pyflow_nodes.Robinson.Nodes.Misc import RobinsonQtComponent
from robinson_flow.pyflow_nodes.Robinson.Nodes.OpenCV import FrameView
import cv2

from robinson_flow.pyflow_nodes.Robinson.Nodes.utils import EvalNode, LoggingView

import datetime
from pathlib import Path

class UIEvalView(UINodeBase):

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

class UIRobinsonView(UINodeBase):
#     pinCreated = QtCore.Signal(object)

    def __init__(self, raw_node):
        super(UIRobinsonView, self).__init__(raw_node)
        actionAddOut = self._menu.addAction("reload")
        iconfile = str((Path(__file__).parent / "resources/reload_icon.svg").resolve())
        actionAddOut.setData(NodeActionButtonInfo(iconfile))
        actionAddOut.triggered.connect(self.update_component)
        self.node = raw_node
        self.component:RobinsonQtComponent = raw_node.component
        self.resizable = True


    def update_component(self):

        self.node.create_component()


class UIRobinsonQtView(UINodeBase):
#     pinCreated = QtCore.Signal(object)

    def __init__(self, raw_node):
        super(UIRobinsonQtView, self).__init__(raw_node)
        actionAddOut = self._menu.addAction("reload")
        iconfile = str((Path(__file__).parent / "resources/reload_icon.svg").resolve())
        actionAddOut.setData(NodeActionButtonInfo(iconfile))
        actionAddOut.triggered.connect(self.update_widget)
        self.node = raw_node
        self.component:RobinsonQtComponent = raw_node.component
        self.resizable = True

        self.component.init()
        # self.update_widget()
        self.addWidget(self.component.get_widget(self))

    def update_widget(self):

        layout = self.customLayout
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)

            if item.widget() is not None:
                item.widget().deleteLater()
                item.widget().setParent(None)
            elif item.layout() is not None:
                clearLayout(item.layout())

            layout.removeItem(item)


        self.node.create_component()
        self.component = self.node.component

        self.addWidget(self.component.get_widget(self))

        self.updateNodeShape()
