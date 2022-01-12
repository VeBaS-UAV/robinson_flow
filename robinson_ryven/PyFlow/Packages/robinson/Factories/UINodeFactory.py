from robinson_ryven.PyFlow.Packages.robinson.Nodes.DemoNode import DemoNode
from robinyon_ryven.PyFlow.Packages.robinson.UI.UIDemoNode import UIDemoNode
from PyFlow.UI.Canvas.UINodeBase import UINodeBase


def createUINode(raw_instance):
    if isinstance(raw_instance, DemoNode):
        return UIDemoNode(raw_instance)
    return UINodeBase(raw_instance)
