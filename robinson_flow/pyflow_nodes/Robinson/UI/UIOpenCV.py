
from PyFlow.UI.Canvas.UINodeBase import UINodeBase
from PyFlow.UI.Widgets.SelectPinDialog import SelectPinDialog
# from PyFlow.Core.ExternalManager import ExternalManagerSingleton
from PyFlow.UI.Utils.stylesheet import Colors
from PyFlow.UI import RESOURCES_DIR
from PyFlow.UI.Canvas.UICommon import *
from vebas.tracking.components.cv import ImageView
from Qt.QtWidgets import QTextEdit, QLineEdit, QLabel
from Qt.QtGui import QImage, QPixmap
from Qt.QtCore import Qt
from robinson_flow.pyflow_nodes.Robinson.Nodes.ExternalNodes import ExternalSource
from robinson_flow.pyflow_nodes.Robinson.Nodes.OpenCV import FrameView
import cv2

#TODO remove opencv nodes
class UIFrameView(UINodeBase):
#     pinCreated = QtCore.Signal(object)

    def __init__(self, raw_node):
        super(UIFrameView, self).__init__(raw_node)
        self.node:FrameView = raw_node
        self.node.image_received.connect(self.image_updated)

        self.resizable = True

        self.image_label = QLabel()
        self.image_label.setText("waiting for image")
        self.image_label.resize(30,30)
        self.addWidget(self.image_label)
        # self.updateSize()

    def updateSize(self):
        scaledPixmap = self.pixmap.scaledToWidth(
            self.customLayout.geometry().width())
        self.Imagelabel.setPixmap(scaledPixmap)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def image_updated(self):
        # print("received image")
        try:
            frame = self.node.frame
            self.pixmap = self.convert_cv_qt(frame)
            self.image_label.setPixmap(self.pixmap)
        except Exception as e:
            print(e)
