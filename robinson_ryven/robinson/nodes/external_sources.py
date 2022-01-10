#!/usr/bin/env python3

from .external_sources_widgets import *
from robinson_ryven.robinson.base import RobinsonRyvenNode
from ryvencore.NodePortBP import NodeInputBP, NodeOutputBP

from PyQt5.QtCore import pyqtSignal
from robinson_ryven.robinson.utils import getLogger

class ExternalSource(RobinsonRyvenNode):

    title = "External Source"
    color = '#e06c78'
    # this one gets automatically created once for each object
    main_widget_class = ExternalSourceWidget
    main_widget_pos = 'between ports'  # alternatively 'between ports'
    # main_widget_pos = 'below ports'  # alternatively 'between ports'

    topic_changed = pyqtSignal(RobinsonRyvenNode)
    # you can use those for your data inputs
    # input_widget_classes = {
        # 'topic_widget': widgets.ExternalSourceInputTopicWidget
    # }

    init_inputs = [
        # NodeInputBP(label='', add_data={'widget name': 'topic_widget', 'widget pos': 'besides'})
        # NodeInputBP(label='')
    ]

    init_outputs = [
        NodeOutputBP(label='')
    ]

    def __init__(self, params):
        super().__init__(params)
        self.logger = getLogger(self)
        self.topic = None
        # self.topic_type = None

    def get_topic(self):
        return self.topic

    def set_topic(self, topic):
        self.topic = topic
        self.topic_changed.emit(self)

    def receive_msg(self, msg):
        self.logger.info(f"receive msg {msg}")
        self.set_output_val(0,msg)
    # def get_topic_type(self):
    #    return self.topic_type

    # def set_topic_type(self, topic):
    #     self.topic_type = topic
    #     # self.topic_changed.emit(self)

class ExternalSink(RobinsonRyvenNode):

    title = "External Sink"
    color = '#DC8665'
    # this one gets automatically created once for each object
    main_widget_class = ExternalSinkWidget
    main_widget_pos = 'between ports'  # alternatively 'between ports'

    topic_changed = pyqtSignal(RobinsonRyvenNode)
    # you can use those for your data inputs
    input_widget_classes = {
        # 'topic_widget': widgets.ExternalSinkTopicWidget
    }

    init_inputs = [
        # NodeInputBP(label='', add_data={'widget name': 'topic_widget', 'widget pos': 'besides'})
        NodeInputBP(label='')
    ]

    init_outputs = [
        # NodeOutputBP(label='')
    ]

    external_output = pyqtSignal(object)

    def __init__(self, params):
        super().__init__(params)
        self.logger = getLogger(self)

        # self.create_input("topic", add_data={'widget name': 'my inp widget', 'widget pos': 'beside'})
        # self.create_output("output")

        self.topic = None

    def get_topic(self):
        return self.topic

    def set_topic(self, topic):
        self.topic = topic
        self.topic_changed.emit(self)


    def update_event(self, inp=-1):
        self.external_output.emit(self.input(0))
