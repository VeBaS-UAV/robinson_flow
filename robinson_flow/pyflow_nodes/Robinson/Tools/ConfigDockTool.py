from robinson.components import Component
from robinson_flow.pyflow_nodes.Robinson.Nodes.BaseNode import RobinsonPyFlowBase

from PyFlow.UI.Tool.Tool import DockTool

from Qt import QtGui, QtWidgets
from Qt.QtGui import QImage, QPixmap, QFont
from Qt.QtWidgets import *
import json
import toml
import yaml


class ConfigDockTool(DockTool):
    """docstring for History tool."""

    def __init__(self):
        super(ConfigDockTool, self).__init__()

        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)

        self.config_widget = QPlainTextEdit()
        self.layout.addWidget(self.config_widget)

        self.lbl_msg = QLabel()
        font = QFont()
        font.setPointSize(8)
        self.lbl_msg.setStyleSheet("color: red")
        self.lbl_msg.setFont(font)
        self.layout.addWidget(self.lbl_msg)

        self.btn_update = QPushButton("update")
        self.btn_update.clicked.connect(self.update_config)
        self.layout.addWidget(self.btn_update)

        self.setWidget(self.widget)

        self.selected_node = None
        self.selected_component = None

    def onShow(self):
        super().onShow()
        # self.pyFlowInstance.canvasWidget.canvas.scene().focusItemChanged.connect(self.selection_changed)
        self.pyFlowInstance.canvasWidget.canvas.scene().selectionChanged.connect(
            self.selection_changed
        )

    # self.pyFlowInstance

    def update_config(self):

        try:
            cfg_text = self.config_widget.toPlainText()
            cfg_dict = toml.loads(cfg_text)

            if self.selected_component is not None:
                self.selected_component.config_update(**cfg_dict)
        except Exception as e:
            self.lbl_msg.setText(str(e))

    def selection_changed(self, *args, **kwargs):
        nodes = self.pyFlowInstance.canvasWidget.canvas.selectedNodes()

        if len(nodes) > 0:
            self.selected_node = nodes[0]._rawNode
            self.selected_component = None
        else:
            self.selected_node = None
            self.selected_component = None
        self.update_widget()

    def update_widget(self):
        if self.selected_node is None:
            self.config_widget.setPlainText("")
            return

        if issubclass(self.selected_node.__class__, RobinsonPyFlowBase):
            self.selected_component = self.selected_node.component

            cfg_dict = None
            try:
                cfg_dict = self.selected_component.config_get()
            except Exception as e:
                print(f"Could not get config from component {self.selected_component}")

            if cfg_dict is not None:
                cfg_text = toml.dumps(self.selected_component.config_get())

                self.config_widget.setPlainText(cfg_text)
            else:
                self.config_widget.setPlainText("")
        else:
            self.config_widget.setPlainText("")

        # QtGui.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()

    @staticmethod
    def getIcon():
        return QtGui.QIcon(":brick.png")

    @staticmethod
    def toolTip():
        return "Robinson Config Tool!"

    @staticmethod
    def name():
        return str("RobinsonDockTool")
