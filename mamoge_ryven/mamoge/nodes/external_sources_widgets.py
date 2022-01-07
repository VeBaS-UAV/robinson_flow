#!/usr/bin/env python3

from ryvencore_qt import \
        Node as Node, \
        IWB as IWB, \
        MWB as MWB

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QSlider
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics, QFont


class ExternalSinkWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)

        self.setLayout(QHBoxLayout())
        self.topic = QLineEdit()

        self.setStyleSheet('''
            QWidget{
                color: white;
                background: transparent;
                border-radius: 4px;
            }
                    ''')
        self.topic.setFont(QFont('source code pro', 10))

        self.topic.setPlaceholderText('topic')

        self.topic.editingFinished.connect(self.topic_changed)

        self.layout().addWidget(self.topic)

    def get_state(self) -> dict:
        print("getting state")
        return {
            'topic': self.topic.text()
        }

    def set_state(self, data: dict):
        self.topic.setText(data['topic'])
        self.topic_changed()
        pass

    def topic_changed(self):
        self.node.set_topic(self.topic.text())

class ExternalSourceWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)

        self.setLayout(QHBoxLayout())
        self.topic = QLineEdit()
        # self.topic_type = QLineEdit()

        self.setStyleSheet('''
            QWidget{
                color: white;
                background: transparent;
                border-radius: 4px;
            }
                    ''')
        self.topic.setFont(QFont('source code pro', 10))
        self.topic.setPlaceholderText('topic')
        self.topic.editingFinished.connect(self.topic_changed)

        self.layout().addWidget(self.topic)

        # self.topic_type.setFont(QFont('source code pro', 10))
        # self.topic_type.setPlaceholderText('topic_type')
        # self.topic_type.editingFinished.connect(self.type_changed)

        # self.layout().addWidget(self.topic_type)

    def get_state(self) -> dict:
        print("getting state")
        return {
            'topic': self.topic.text()
        }

    def set_state(self, data: dict):
        self.topic.setText(data['topic'])
        self.topic_changed()
        pass

    def topic_changed(self):
        self.node.set_topic(self.topic.text())

from PyQt5.QtWidgets import QLabel, QPushButton, QFileDialog, QVBoxLayout, QWidget, QTextEdit
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import QSize, QTimer

import cv2
import os

class WebcamFeedWidget(MWB, QWidget):
    capture_device = None

    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)


        self.video_size = QSize(400, 300)
        self.timer = QTimer(self)
        self.capture = None

        self.image_label = QLabel()
        self.image_label.setFixedSize(self.video_size)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.image_label)
        self.setLayout(self.main_layout)

        self.setup_camera()

        self.resize(self.video_size)

    def setup_camera(self):
        if WebcamFeedWidget.capture_device is None:
            WebcamFeedWidget.capture_device = cv2.VideoCapture(0)
        self.capture = WebcamFeedWidget.capture_device
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_size.width())
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_size.height())

        self.timer.timeout.connect(self.display_video_stream)
        self.timer.start(20)

    def display_video_stream(self):
        try:
            _, frame = self.capture.read()
        except:
            return
        if frame is None:
            return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # frame = cv2.flip(frame, 1)
        image = QImage(frame, frame.shape[1], frame.shape[0],
                       frame.strides[0], QImage.Format_RGB888)
        scaled_image = image.scaled(self.video_size)
        self.image_label.setPixmap(QPixmap.fromImage(scaled_image))

        self.node.video_picture_updated(frame)

    def remove_event(self):
        self.timer.stop()

class OpenCVNode_MainWidget(MWB, QLabel):
    def __init__(self, params):
        MWB.__init__(self, params)
        QLabel.__init__(self)

        self.resize(200, 200)

    def show_image(self, img):
        self.resize(200, 200)

        try:
            rgb_image = img #cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        except cv2.error:
            return

        if len(rgb_image.shape) == 0:
            return
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        img_w = qt_image.width()
        img_h = qt_image.height()
        proportion = img_w / img_h
        self.resize(int(self.width() * proportion), int(self.height()))
        qt_image = qt_image.scaled(self.width(), self.height())
        self.setPixmap(QPixmap(qt_image))
        self.node.update_shape()
