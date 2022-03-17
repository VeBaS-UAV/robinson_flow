from robinson_flow.pyflow_nodes.Robinson.Nodes.BaseNode import RobinsonProfiler, RobinsonPyFlowBase, RobinsonTicker
from robinson_flow.pyflow_nodes.Robinson.Nodes.ExternalNodes import ExternalSink, ExternalSource
from robinson_flow.pyflow_nodes.Robinson.Nodes.Misc import RobinsonQtComponent
from robinson_flow.pyflow_nodes.Robinson.Nodes.OpenCV import FrameView
from robinson_flow.pyflow_nodes.Robinson.Nodes.utils import EvalNode, LoggingView, PlotView
from robinson_flow.pyflow_nodes.Robinson.UI.UIExternalNode import UIExternalSink, UIExternalSource
from PyFlow.UI.Canvas.UINodeBase import UINodeBase

from robinson_flow.pyflow_nodes.Robinson.UI.UIOpenCV import UIFrameView
from robinson_flow.pyflow_nodes.Robinson.UI.UIutils import UIEvalView, UILoggingView, UIRobinsonPlotView, UIRobinsonProfilerView, UIRobinsonQtView, UIRobinsonTickerView, UIRobinsonView



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
    if isinstance(raw_instance, RobinsonProfiler):
        return UIRobinsonProfilerView(raw_instance)
    if isinstance(raw_instance, RobinsonTicker):
        return UIRobinsonTickerView(raw_instance)
    if isinstance(raw_instance, EvalNode):
        return UIEvalView(raw_instance)
    if isinstance(raw_instance, PlotView):
        return UIRobinsonPlotView(raw_instance)
    if isinstance(raw_instance, RobinsonPyFlowBase):
        component = raw_instance.component
        if isinstance(component, RobinsonQtComponent):
            return UIRobinsonQtView(raw_instance)
        else:
            return UIRobinsonView(raw_instance)

    return UINodeBase(raw_instance)
