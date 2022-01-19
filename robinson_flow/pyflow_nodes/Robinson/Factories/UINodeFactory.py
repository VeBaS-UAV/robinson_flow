from vebas.tracking.components.cv import ImageView
from robinson_flow.pyflow_nodes.Robinson.Nodes.BaseNode import RobinsonTicker
from robinson_flow.pyflow_nodes.Robinson.Nodes.ExternalNodes import ExternalSink, ExternalSource
from robinson_flow.pyflow_nodes.Robinson.Nodes.OpenCV import FrameView
from robinson_flow.pyflow_nodes.Robinson.Nodes.utils import LambdaNode, LoggingView
from robinson_flow.pyflow_nodes.Robinson.UI.UIExternalNode import UIExternalSink, UIExternalSource
from PyFlow.UI.Canvas.UINodeBase import UINodeBase

from robinson_flow.pyflow_nodes.Robinson.UI.UIOpenCV import UIFrameView
from robinson_flow.pyflow_nodes.Robinson.UI.UIutils import UILambdaView, UILoggingView, UIRobinsonTickerView



def createUINode(raw_instance):
    # if isinstance(raw_instance, DemoNode):
        # return UIDemoNode(raw_instance)
    if isinstance(raw_instance, ExternalSource):
        return UIExternalSource(raw_instance)
    if isinstance(raw_instance, ExternalSink):
        return UIExternalSink(raw_instance)
    if isinstance(raw_instance, FrameView):
        return UIFrameView(raw_instance)
    if isinstance(raw_instance, LoggingView):
        return UILoggingView(raw_instance)
    if isinstance(raw_instance, LambdaNode):
        return UILambdaView(raw_instance)
    if isinstance(raw_instance, RobinsonTicker):
        return UIRobinsonTickerView(raw_instance)

    return UINodeBase(raw_instance)
