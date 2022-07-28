from PyFlow.Core.Common import PinOptions
from PyFlow.Core.NodeBase import NodeBase
from pydantic.main import BaseModel

from robinson.components import Component, DataPortOutput
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

            frame = self.frame
            self.pixmap = self.convert_cv_qt(frame)
            self.image_label.setPixmap(self.pixmap)
            print(e)

class FrameView(ImageView):

    pass

import numpy as np

class OpticalFlowDense(Component):



    def __init__(self, name: str, fqn_logger=True):
        super().__init__(name, fqn_logger)

        self.dataport_output_image = DataPortOutput("image")

        self.prev_frame = None
        self.frame = None

    def dataport_input_image(self, msg):
        self.frame= msg


    def update(self):
        if self.frame is None:
            return

        if self.prev_frame is None:
            self.prev_frame = self.frame
            self.frame = None
            return

        hsv = np.zeros_like(self.frame)
        hsv[..., 1] = 255
        next = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        prev = cv2.cvtColor(self.prev_frame, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(prev, next, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])


        hsv[..., 0] = ang*180/np.pi/2
        hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        self.dataport_output_image(bgr)

class ImageSource(Component):
    class Config(BaseModel):
        video_file:str = ""

    config = Config()

    def config_update(self, **kw_args):
        self.config = ImageSource.Config(**{**self.config.dict(), **kw_args})
        self.init()

    def config_get(self, key=None):
        if key is None:
            return self.config.dict()
        if key not in self.config.dict():
            return None
        return self.config[key]

    def __init__(self, name: str, fqn_logger=True):
        super().__init__(name, fqn_logger)
        self.dataport_output_frame = DataPortOutput("frame")

        self.img = None

        self.is_init = False

        # self.config.video_file = '/home/matthias/tmp/vebas/uav_t67_2022-05-05/DJI_0012.MP4'

    def dataport_input_filename(self, msg):
        self.config.video_file = msg
        self.is_init = False

    def init(self):
        self.img = cv2.imread(self.config.video_file)
        self.is_init = True

    def update(self):

        if self.is_init == False:
            self.init()

        if self.img is not None:
            self.dataport_output_frame(self.img)

class VideoSource(Component):


    class Config(BaseModel):
        video_file:str = ""

    config = Config()

    def config_update(self, **kw_args):
        self.config = VideoSource.Config(**{**self.config.dict(), **kw_args})
        self.init()

    def config_get(self, key=None):
        if key is None:
            return self.config.dict()
        if key not in self.config.dict():
            return None
        return self.config[key]

    def __init__(self, name: str, fqn_logger=True):
        super().__init__(name, fqn_logger)
        self.dataport_output_frame = DataPortOutput("frame")

        self.cap = None

        self.is_init = False

        # self.config.video_file = '/home/matthias/tmp/vebas/uav_t67_2022-05-05/DJI_0012.MP4'

    def dataport_input_filename(self, msg):
        self.config.video_file = msg
        self.is_init = False

    def dataport_input_restart(self, msg):
        self.init()


    def dataport_input_goto_frame(self, msg):
        if msg < 1:
            total = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            val = int(msg * total)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, val)
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, msg)

    def init(self):
        self.cap = cv2.VideoCapture(self.config.video_file)
        self.is_init = True

    def update(self):

        if self.is_init == False:
            self.init()

        ret, frame = self.cap.read()
        if ret == True:
            self.dataport_output_frame(frame)
        else:
            self.init()
