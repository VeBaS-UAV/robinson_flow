from PyFlow.Core.Common import PinOptions
from PyFlow.Core.NodeBase import NodeBase

from PyQt5.QtCore import pyqtSignal, QObject

from robinson_flow.logger import getNodeLogger


class FrameView(NodeBase, QObject):

    _packageName = "robinson"
    connections:dict = {}

    image_received = pyqtSignal()

    def __init__(self, name, uid=None):
        super().__init__(name, uid)
        self.logger = getNodeLogger(self)

        self.frame = None
        self.inp = self.createInputPin("img", "AnyPin", None)
        self.inp.enableOptions(PinOptions.AllowAny)
        self.inp.dataBeenSet.connect(self.img_received_callback)

    def img_received_callback(self, *args):
        self.frame = self.inp.getData()
        self.image_received.emit()

    @staticmethod
    def category():
        return "OpenCV"
