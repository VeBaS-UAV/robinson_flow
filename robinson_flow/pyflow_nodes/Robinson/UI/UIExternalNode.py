
## Copyright 2015-2019 Ilgar Lunin, Pedro Cabrera

## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at

##     http://www.apache.org/licenses/LICENSE-2.0

## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.


from Qt import QtCore

from PyFlow.UI.Canvas.UINodeBase import UINodeBase
from PyFlow.UI.Widgets.SelectPinDialog import SelectPinDialog
# from PyFlow.Core.ExternalManager import ExternalManagerSingleton
from PyFlow.UI.Utils.stylesheet import Colors
from PyFlow.UI import RESOURCES_DIR
from PyFlow.UI.Canvas.UICommon import *
from Qt.QtWidgets import QTextEdit, QLineEdit
from robinson_flow.pyflow_nodes.Robinson.Nodes.ExternalNodes import ExternalSource

class UIExternalSource(UINodeBase):

    def __init__(self, raw_node):
        super(UIExternalSource, self).__init__(raw_node)
        self.node:ExternalSource = raw_node

    def createInputWidgets(self, inputsCategory, inGroup=None, pins=True):
        preIndex = inputsCategory.Layout.count()
        w = super().createInputWidgets(inputsCategory, inGroup, pins)

        self.topic_text = QLineEdit()
        self.topic_text.setText(self.node.topic)
        self.topic_text.editingFinished.connect(self.topic_changed)

        inputsCategory.insertWidget(preIndex, "Topic", self.topic_text, group=inGroup)

    def topic_changed(self, *args):
        self.node.update_topic(self.topic_text.text())

class UIExternalSink(UINodeBase):

    def __init__(self, raw_node):
        super(UIExternalSink, self).__init__(raw_node)
        self.node:ExternalSource = raw_node

    def createInputWidgets(self, inputsCategory, inGroup=None, pins=True):
        preIndex = inputsCategory.Layout.count()
        w = super().createInputWidgets(inputsCategory, inGroup, pins)

        self.topic_text = QLineEdit()
        self.topic_text.setText(self.node.topic)
        self.topic_text.editingFinished.connect(self.topic_changed)

        inputsCategory.insertWidget(preIndex, "Topic", self.topic_text, group=inGroup)

    def topic_changed(self, *args):
        self.node.update_topic(self.topic_text.text())
