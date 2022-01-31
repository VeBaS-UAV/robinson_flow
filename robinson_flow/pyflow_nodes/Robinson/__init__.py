PACKAGE_NAME = 'Robinson'

from robinson.components import Component
from collections import OrderedDict

from PyFlow.UI.UIInterfaces import IPackage
import robinson_flow
from robinson_flow.pyflow_nodes.Robinson.Factories.PinInputWidgetFactory import getInputWidget
from robinson_flow.pyflow_nodes.Robinson.Factories.UINodeFactory import createUINode
from robinson_flow.pyflow_nodes.Robinson.Nodes.BaseNode import RobinsonPyFlowBase, RobinsonPyFlowFunc, RobinsonTicker
from robinson_flow.pyflow_nodes.Robinson.Nodes.ExternalNodes import ExternalSink, ExternalSource
from robinson_flow.pyflow_nodes.Robinson.Nodes.OpenCV import FrameView
from robinson_flow.pyflow_nodes.Robinson.Nodes.utils import EvalNode, LambdaNode, LoggingView, OnMessageExec, PlotView

# # Pins
from robinson_flow.pyflow_nodes.Robinson.Pins.MavlinkPin import MavlinkPin

# # Function based nodes
# # from robinson_flow.pyflow_nodes.Robinson.FunctionLibraries.DemoLib import DemoLib

# # Tools
# from robinson_flow.pyflow_nodes.Robinson.Tools.DemoShelfTool import DemoShelfTool
# from robinson_flow.pyflow_nodes.Robinson.Tools.DemoDockTool import DemoDockTool

# # Exporters
# # from robinson_flow.pyflow_nodes.Robinson.Exporters.DemoExporter import DemoExporter

# # Factories
# # from robinson_flow.pyflow_nodes.Robinson.Factories.UIPinFactory import createUIPin
# # from robinson_flow.pyflow_nodes.Robinson.Factories.UINodeFactory import createUINode
# from robinson_flow.pyflow_nodes.Robinson.Factories.PinInputWidgetFactory import getInputWidget
# # Prefs widgets
# from robinson_flow.ryven_nodes.nodes.components import PrintOutputComponent, TestComponent

# from robinson_flow.pyflow_nodes.Robinson.Nodes.ExternalNodes import ExternalSink, ExternalSource
# from robinson_flow.pyflow_nodes.Robinson.Nodes.BaseNode import AddHelloComponent, OutputNameComponent, RobinsonPyFlowBase, RobinsonPyFlowFunc, RobinsonTicker

_FOO_LIBS = {}
_NODES = {}
_PINS = {}
_TOOLS = OrderedDict()
_PREFS_WIDGETS = OrderedDict()
_EXPORTERS = OrderedDict()

# _FOO_LIBS[DemoLib.__name__] = DemoLib(PACKAGE_NAME)

_PINS[MavlinkPin.__name__] = MavlinkPin

# _TOOLS[DemoShelfTool.__name__] = DemoShelfTool
# _TOOLS[DemoDockTool.__name__] = DemoDockTool

# _EXPORTERS[RobinsonExporter.__name__] = RobinsonExporter

# _PREFS_WIDGETS["Demo"] = DemoPrefs

# import inspect
# import sys


def factory(cls):
    name = cls.__name__
    if name.endswith("Component"):
        name = name[:-len("Component")]

    name = name.strip("_/-")
    # print(f"generate component {name}:{cls}")
    class PyflowTemplateNode(RobinsonPyFlowBase):
        def __init__(self, name, uid=None):
            super().__init__(name, cls=cls, uid=uid)

        @staticmethod
        def category():
            return cls.__module__.replace(".","|")

    cl =  PyflowTemplateNode
    cl.__name__ = name

    return name, cl

def factory_function(cb):
    name = cb.__name__

    # print(f"generate component {name}:{cls}")
    class RobinsonPyFlowFunctionWrapperFactory(RobinsonPyFlowFunc):
        def __init__(self, name, uid=None):
            super().__init__(name, cb=cb, uid=uid)

        @staticmethod
        def category():
            return cb.__module__.replace(".","|")


    cl =  RobinsonPyFlowFunctionWrapperFactory
    cl.__name__ = name

    return name, cl


def load_components_from_module(module):
    import inspect
    import sys
    results =  []
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            if sys.modules[obj.__module__] == module:
                if issubclass(obj, Component):
                    results.append(obj)
    return results

def export_nodes():
    import importlib
    from robinson_flow.config import settings

    robinson_packages = []
    component_list = []
    function_list = []

    try:
        robinson_packages = settings.robinson.modules


        for rob_pkg in robinson_packages:
            try:
                module = importlib.import_module(rob_pkg)
                component_list.extend(load_components_from_module(module))
            except Exception as e:
                print("Could not load module")
                print(e)

    except Exception as e:
        print("Could not load robinson components from config")
        print(e)


    rob_comps = {k:v for k,v in [factory(c) for c in component_list]}

    function_names = []
    try:
        function_names = settings.robinson.functions #.append("")

        for rob_pkg in function_names:
            module = ".".join(rob_pkg.split(".")[:-1])
            name = rob_pkg.split(".")[-1]
            module = importlib.import_module(module)
            func = getattr(module, name)
            function_list.append(func)
    except Exception as e:
        print("Could not load function from module")
        print(e)

    func_comps = {k:v for k,v in [factory_function(f) for f in function_list]}

    other_comp = {}

    other_comp["ExternalSource"] = ExternalSource
    other_comp["ExternalSink"] = ExternalSink
    other_comp["FrameView"] = FrameView
    other_comp["LambdaNode"] = LambdaNode
    other_comp["LoggingView"] = LoggingView
    other_comp["RobinsonTicker"] = RobinsonTicker
    other_comp["OnMessageExec"] = OnMessageExec
    other_comp["EvalNode"] = EvalNode
    other_comp["PlotView"] = PlotView

    return {**rob_comps, **func_comps, **other_comp}

class Robinson(IPackage):
	def __init__(self):
		super(Robinson, self).__init__()

	@staticmethod
	def GetExporters():
		return _EXPORTERS

	@staticmethod
	def GetFunctionLibraries():
		return _FOO_LIBS

	@staticmethod
	def GetNodeClasses():
		return export_nodes()

	@staticmethod
	def GetPinClasses():
		return _PINS

	@staticmethod
	def GetToolClasses():
		return _TOOLS

	@staticmethod
	def UIPinsFactory():
		return None#createUIPin

	@staticmethod
	def UINodesFactory():
		return createUINode

	@staticmethod
	def PinsInputWidgetFactory():
		return getInputWidget

	@staticmethod
	def PrefsWidgets():
		return _PREFS_WIDGETS

