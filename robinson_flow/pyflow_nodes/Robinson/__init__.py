PACKAGE_NAME = 'Robinson'

from robinson.components import Component
from collections import OrderedDict

from PyFlow.UI.UIInterfaces import IPackage
import robinson_flow
from robinson_flow.pyflow_nodes.Robinson.Exporters.RobinsonExporter import RobinsonExporter
from robinson_flow.pyflow_nodes.Robinson.Factories.PinInputWidgetFactory import getInputWidget
from robinson_flow.pyflow_nodes.Robinson.Factories.UINodeFactory import createUINode

# # Pins
from robinson_flow.pyflow_nodes.Robinson.Pins.MavlinkPin import MavlinkPin
from robinson_flow.pyflow_nodes.Robinson.Tools.ConfigDockTool import ConfigDockTool

from robinson_flow.pyflow_nodes.Robinson.package_utils import export_nodes
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


_FOO_LIBS = {}
_NODES = {}
_PINS = {}
_TOOLS = OrderedDict()
_PREFS_WIDGETS = OrderedDict()
_EXPORTERS = OrderedDict()

# _FOO_LIBS[DemoLib.__name__] = DemoLib(PACKAGE_NAME)

_PINS[MavlinkPin.__name__] = MavlinkPin

# _TOOLS[DemoShelfTool.__name__] = DemoShelfTool
_TOOLS[ConfigDockTool.__name__] = ConfigDockTool

_EXPORTERS[RobinsonExporter.__name__] = RobinsonExporter

# _PREFS_WIDGETS["Demo"] = DemoPrefs


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

