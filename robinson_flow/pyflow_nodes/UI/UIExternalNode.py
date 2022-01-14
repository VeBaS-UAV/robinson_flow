
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
from robinson_flow.pyflow_nodes.Nodes.ExternalNodes import ExternalSource

class UIExternalSource(UINodeBase):
#     pinCreated = QtCore.Signal(object)

    def __init__(self, raw_node):
        super(UIExternalSource, self).__init__(raw_node)
        self.node:ExternalSource = raw_node
        print("UIExternalSource.__init__")

    def createInputWidgets(self, inputsCategory, inGroup=None, pins=True):
        print(f"createInputWidgets(self, {inputsCategory}, {inGroup}, {pins}")
        preIndex = inputsCategory.Layout.count()
        w = super().createInputWidgets(inputsCategory, inGroup, pins)

        self.topic_text = QLineEdit()
        self.topic_text.setText(self.node.topic)
        self.topic_text.editingFinished.connect(self.topic_changed)

        inputsCategory.insertWidget(preIndex, "Topic", self.topic_text, group=inGroup)

    def topic_changed(self, *args):
        print(f"topic_changed {args}")
        self.node.update_topic(self.topic_text.text())

    # def createOutputWidgets(self, inputsCategory, headName="Outputs"):
        # print("createOutputWidget", inputsCategory, headName)
        # return super().createOutputWidgets(inputsCategory, headName)

        # self.topic_edit = QButton()
        # self.topic_edit.setText(topic)
        # self.addWidget(self.topic_edit)
        # self.topic_edit.textChanged.connect(self.topic_change
# class UIExternalInputs(UINodeBase):
#     pinCreated = QtCore.Signal(object)

#     def __init__(self, raw_node):
#         super(UIExternalInputs, self).__init__(raw_node)
#         actionAddOut = self._menu.addAction("Add pin")
#         actionAddOut.setData(NodeActionButtonInfo(RESOURCES_DIR + "/pin.svg"))
#         actionAddOut.triggered.connect(self.createPinDialog)
#         self.color = Colors.DarkGray
#         self.headColorOverride = Colors.Gray
#         self.image = RESOURCES_DIR + "/gear.svg"

#     def setName(self, name):
#         oldName = self.getName()
#         super(UIExternalInputs, self).setName(name)
#         owningCompoundNode = self.canvasRef().graphManager.findNode(
#             self._rawNode.graph().name)
#         if owningCompoundNode:
#             uiCompoundNode = owningCompoundNode.getWrapper()
#             if oldName in uiCompoundNode.groups["input"]:
#                 grpItem = uiCompoundNode.groups["input"][oldName]
#                 grpItem.name = name
#             if oldName in owningCompoundNode.groups["input"]:
#                 for inp in owningCompoundNode.groups["input"][oldName]:
#                     inp.grop = name
#                 owningCompoundNode.groups["input"][name] = owningCompoundNode.groups["input"].pop(oldName)

#     def createPinDialog(self):
#         self.d = SelectPinDialog()
#         self.d.exec_()
#         dataType = self.d.getResult()
#         if dataType is not None:
#             self.onAddOutPin(None, dataType)

#     def onAddOutPin(self, name=None, dataType="AnyPin"):
#         rawPin = self._rawNode.addOutPin(name, dataType)
#         uiPin = self._createUIPinWrapper(rawPin)
#         uiPin.labelColor = Colors.AbsoluteBlack
#         self.pinCreated.emit(uiPin)
#         self.updateNodeShape()
#         return uiPin

#     def postCreate(self, jsonTemplate):
#         # this call will create wrappers for raw pins
#         UINodeBase.postCreate(self, jsonTemplate)

#         for uiPin in self.UIPins.values():
#             uiPin.labelColor = Colors.AbsoluteBlack

    # def createInputWidgets(self, inputsCategory, inGroup=None, pins=True):
        # if self.graph() == ExternalManagerSingleton().get().findRootExternal():
        # self.createOutputWidgets(inputsCategory, inGroup)

# class UIExternalOutputs(UINodeBase):
#     pinCreated = QtCore.Signal(object)

#     def __init__(self, raw_node):
#         super(UIExternalOutputs, self).__init__(raw_node)
#         actionAddOut = self._menu.addAction("Add pin")
#         actionAddOut.setData(NodeActionButtonInfo(RESOURCES_DIR + "/pin.svg"))
#         actionAddOut.triggered.connect(self.createPinDialog)

#         self.color = Colors.DarkGray
#         self.headColorOverride = Colors.Gray
#         self.image = RESOURCES_DIR + "/gear.svg"

#     def setName(self, name):
#         oldName = self.getName()
#         super(UIExternalOutputs, self).setName(name)
#         owningCompoundNode = self.canvasRef().graphManager.findNode(
#             self._rawNode.graph().name)
#         if owningCompoundNode:
#             uiCompoundNode = owningCompoundNode.getWrapper()
#             if oldName in uiCompoundNode.groups["output"]:
#                 grpItem = uiCompoundNode.groups["output"][oldName]
#                 grpItem.name = name

#     def createPinDialog(self):
#         self.d = SelectPinDialog()
#         self.d.exec_()
#         dataType = self.d.getResult()
#         if dataType is not None:
#             self.onAddInPin(None, dataType)

#     def onAddInPin(self, name=None, dataType="AnyPin"):
#         rawPin = self._rawNode.addInPin(name, dataType)
#         uiPin = self._createUIPinWrapper(rawPin)
#         uiPin.labelColor = Colors.AbsoluteBlack
#         self.pinCreated.emit(uiPin)
#         self.updateNodeShape()
#         return uiPin

#     def postCreate(self, jsonTemplate):
#         UINodeBase.postCreate(self, jsonTemplate)
#         for uiPin in self.UIPins.values():
#             uiPin.labelColor = Colors.AbsoluteBlack
