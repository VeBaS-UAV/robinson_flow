#!/usr/bin/env python3
from ryvencore.NodePortBP import NodeInputBP, NodeOutputBP
from random import random

import ryvencore_qt as rc
# let's define some nodes
# to easily see something in action, we create one node generating random numbers, and one that prints them

from vebas.components import Component, DataPortOutput, InputOutputPortComponent

import vebas.config
from mamoge_ryven import mamoge

from mamoge_ryven.mamoge.base import MamoGeRyvenWrapper

from .external_sources import *
from .components import export_nodes as component_nodes

# from mamoge_ryven.mamoge.nodes import MamoGeRyvenNode, MamoGeRyvenWrapper
vebas.config.default_logging_settings()

from ryvencore_qt.src.flows.nodes.PortItemInputWidgets import Data_IW_M as Data_IW

class RandNodeRyven(rc.Node):
    """Generates scaled random float values"""

    title = 'Rand(ryven)'
    init_inputs = [
        rc.NodeInputBP(dtype=rc.dtypes.Data(default=1)),
    ]
    init_outputs = [
        rc.NodeOutputBP(),
    ]
    color = '#fcba03'

    def update_event(self, inp=-1):
        print("RandNodeRyven update event")
        # random float between 0 and value at input
        val = random() * float(self.input(0))

        # setting the value of the first output
        self.set_output_val(0, val)

class PrintNodeRyven(rc.Node):
    title = 'Print(ryven)'
    init_inputs = [
        NodeInputBP(),
    ]
    color = '#A9D5EF'

    def update_event(self, inp=-1):
        print("PrintNodeRyven update_event", type(self.input(0)), self.input(0))


# class CVImage:
#     """
#     The OpenCV Mat(rix) data type seems to have overridden comparison operations to perform element-wise comparisons
#     which breaks ryverncore-internal object comparisons.
#     To avoid this, I'll simply use this wrapper class and recreate a new object every time for now, so ryvencore
#     doesn't think two different images are the same.
#     """

#     def __init__(self, img):
#         self.img = img


class WebcamFeed(rc.Node):
    title = 'Webcam Feed'
    init_inputs = []
    init_outputs = [
        NodeOutputBP(),
    ]
    main_widget_class = external_sources.WebcamFeedWidget

    def video_picture_updated(self, frame):
        self.set_output_val(0, frame)


class OpenCVNodeBase(rc.Node):
    title = 'Display Image'
    init_outputs = [
        # NodeOutputBP()
    ]
    init_inputs = [
        NodeInputBP('img'),
    ]
    main_widget_class = external_sources.OpenCVNode_MainWidget
    main_widget_pos = 'below ports'

    def __init__(self, params):
        super().__init__(params)

        if self.session.gui:
            from PyQt5.QtCore import QObject, pyqtSignal
            class Signals(QObject):
                new_img = pyqtSignal(object)

            # to send images to main_widget in gui mode
            # self.SIGNALS = Signals()

    def view_place_event(self):
        # self.SIGNALS.new_img.connect(self.main_widget().show_image)

        try:
            # pass
            self.main_widget().show_image(self.get_img())
            # self.SIGNALS.new_img.emit(self.get_img())
        except:  # there might not be an image ready yet
            pass

    def update_event(self, inp=-1):
        new_img_wrp = self.get_img()

        if self.session.gui:
            # self.SIGNALS.new_img.emit(new_img_wrp)
            self.main_widget().show_image(self.get_img())

        # self.set_output_val(0, new_img_wrp)

    def get_img(self):
        return self.input(0)


class Args(rc.Node):
    title = 'ArgsConcat'
    init_inputs = [
        NodeInputBP("arg_0"),
        NodeInputBP("arg_1"),
    ]
    init_outputs = [
        NodeOutputBP("*args"),
        NodeOutputBP("arg_0, arg_1"),
        NodeOutputBP("**kwargs"),
    ]
    color = '#A9D5EF'

    def update_event(self, inp=-1):
        args = [self.input(i) for i in range(len(self.inputs))]

        try:
            self.set_output_val(0, set(args))
            self.set_output_val(1, tuple(args))
            self.set_output_val(2, dict(arg_0=args[0], arg_1=args[1]))
        except Exception as e:
            self.logger = getLogger(self)
            self.logger.error(e)



def export_nodes():

    nodes = []

    nodes.extend([
        Args,
        ExternalSource,
        ExternalSink,
        WebcamFeed,
        OpenCVNodeBase
    ])

    nodes.extend(component_nodes())


    return nodes
