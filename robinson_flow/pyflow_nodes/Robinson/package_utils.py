from robinson.components import Component
from robinson_flow.pyflow_nodes.Robinson.Nodes.BaseNode import (
    RobinsonPyFlowBase,
    RobinsonTicker,
)
from robinson_flow.pyflow_nodes.Robinson.Nodes.ExternalNodes import (
    ExternalSink,
    ExternalSource,
)
from robinson_flow.pyflow_nodes.Robinson.Nodes.utils import LambdaExpressionComponent

import robinson.config


def factory(cls):
    name = cls.__name__
    if name.endswith("Component"):
        name = name[: -len("Component")]

    name = name.strip("_/-")
    # print(f"generate component {name}:{cls}")
    class PyflowTemplateNode(RobinsonPyFlowBase):
        def __init__(self, name, uid=None):
            super().__init__(name, cls=cls, uid=uid)

        @staticmethod
        def category():
            return cls.__module__.replace(".", "|")

    cl = PyflowTemplateNode
    cl.__name__ = name

    return name, cl


def load_components_from_module(module):
    import inspect
    import sys

    results = []
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            if sys.modules[obj.__module__] == module:
                if issubclass(obj, Component):
                    results.append(obj)
    return results


def export_nodes():
    import importlib

    robinson_packages = []
    component_list = []
    function_list = []

    component_list.append(LambdaExpressionComponent)
    try:
        # robinson_packages = robinson.config.current().robinson.modules

        robinson_packages = [
            "vebas.pyflow",
            "robinson.messaging.mavlink",
            "robinson.components.common",
            "robinson.components.cv",
            "robinson.components.monitors",
            "vebas.mavlink",
            "vebas.mavlink.missiontracker",
            "vebas.tracking.components.cv",
            "vebas.tracking.components.control",
            "vebas.tracking.components.filter",
            "vebas.tracking.components.transform",
            "vebas.tracking.precision_approaching.components",
            "vebas.tracking.target_based",
            "vebas.tracking.gfai",
            "robinson_flow.pyflow_nodes.Robinson.Nodes.Misc",
            "robinson_flow.pyflow_nodes.Robinson.Nodes.utils",
            "robinson_flow.pyflow_nodes.Robinson.Nodes.OpenCV",
        ]

        for rob_pkg in robinson_packages:
            try:
                module = importlib.import_module(rob_pkg)
                component_list.extend(load_components_from_module(module))
            except Exception as e:
                print(f"Could not load module {rob_pkg}")
                print(e)

    except Exception as e:
        print("Could not load robinson components from config")
        print(e)

    rob_comps = {k: v for k, v in [factory(c) for c in component_list]}

    other_comp = {}

    other_comp["ExternalSource"] = ExternalSource
    other_comp["ExternalSink"] = ExternalSink
    other_comp["RobinsonTicker"] = RobinsonTicker

    return {**rob_comps, **other_comp}
