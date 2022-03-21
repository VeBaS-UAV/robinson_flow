from PyFlow.Core.Common import PinOptions
from PyFlow.Core.NodeBase import NodeBase

from PyQt5.QtCore import pyqtSignal, QObject
from robinson.components import Component
from robinson.components.qt import RobinsonQtComponent

from robinson_flow.logger import getNodeLogger

from Qt.QtWidgets import QTextEdit, QLineEdit, QLabel
from Qt.QtGui import QImage, QPixmap
from Qt.QtCore import Qt
import cv2

class ImageView(Component, RobinsonQtComponent):

    def __init__(self, name: str, fqn_logger=True):
        super().__init__(name, fqn_logger)

        self.frame = None

    def dataport_input_frame(self, msg):
        self.frame = msg

    def get_widget(self, parent):
        self.image_label = QLabel()
        self.image_label.setText("waiting for image")
        self.image_label.resize(30,30)

        return self.image_label

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio)

        return QPixmap.fromImage(p)

    def update(self):
        self.image_updated()

    def image_updated(self):
        if self.frame is None:
            return

        try:
            frame = self.frame
            self.pixmap = self.convert_cv_qt(frame)
            self.image_label.setPixmap(self.pixmap)
        except Exception as e:
            print(e)

class FrameView(ImageView):

    pass
