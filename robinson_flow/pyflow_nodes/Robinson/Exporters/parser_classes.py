#!/usr/bin/env python3

import json
from robinson import components
from robinson.messaging.mqtt import MQTTConnection
import yaml
import pickle

from pprint import pprint

from pydantic import BaseModel
from typing import Any, List
import traceback
import ipdb
from robinson.connector import ExternalConnectionHandler
from robinson.components.qt import RobinsonQtComponent

from robinson.messaging.mqtt import MQTTConnection

import importlib


class CDir(BaseModel):
    from_node: Any = None
    from_idx: Any = None
    to_node: Any = None
    to_idx: Any = None

    def from_name(self):
        try:
            return self.from_node.name()
        except Exception as e:
            print(e, self.from_node)
            return str(self.from_node)

    def to_name(self):
        try:
            return self.to_node.name()
        except Exception as e:
            print(e, self.to_node)
            return str(self.to_node)

    def from_port(self):
        try:
            # return self.from_node["robinson"]["output_names"][self.from_idx - 2]
            return self.from_node.output_portname_by_index(self.from_idx)
        except Exception as e:
            print("Error from_port", e, self.from_node, self.from_idx)
            print(traceback.format_exc())
            return str(self.from_idx)

    def to_port(self):
        try:
            # return self.to_node["robinson"]["input_names"][self.to_idx - 2]
            return self.to_node.input_portname_by_index(self.to_idx)

        except Exception as e:
            print("Error to_port", e, self.to_node, self.to_idx)
            print(traceback.format_exc())
            return str(self.to_idx)

    def __repr__(self):
        # ipdb.set_trace()
        return f"Connection({self.from_name()}.{self.from_port()} -> {self.to_name()}.{self.to_port()})"


class PortDefinition:
    def __init__(self, name, data):
        self.name = name
        self.data = data

    def __repr__(self):
        return f"<Port  {self.name}>"


class InputPortDefinition(PortDefinition):
    def __repr__(self):
        return f"<InputPort  {self.name}>"


class OutputPortDefinition(PortDefinition):
    def __repr__(self):
        return f"<OutputPort  {self.name}>"


class NodeDefinition:
    def __init__(self, name, data) -> None:
        self._name = name
        self.data = data

    def __getitem__(self, key):
        # print("__getitem__", key)
        if isinstance(key, int):
            return list(self.data)[key]

        return self.data[key]

    def name(self):
        return self._name

    def is_robinson(self):
        return "robinson" in self.data

    def is_compound(self):
        return "graphData" in self.data

    def is_external_source(self):
        return "type" in self.data and self.data["type"] == "ExternalSource"

    def is_external_sink(self):
        return "type" in self.data and self.data["type"] == "ExternalSink"

    def is_external(self):
        return self.is_external_sink() or self.is_external_source()

    def is_graph_input(self):
        return "type" in self.data and self.data["type"] == "graphInputs"

    def is_graph_output(self):
        return "type" in self.data and self.data["type"] == "graphOutputs"

    def is_graph_port(self):
        return self.is_graph_input() or self.is_graph_output()

    def _nodes(self):
        if "nodes" in self.data:
            nodes = self.data["nodes"]
            nodes = {n["uuid"]: NodeDefinition(n["name"], n) for n in nodes}
            return nodes
        return {}

    def robinson_nodes(self):
        nodes = [n for n in self._nodes().values() if n.is_robinson()]
        nodes = {n["uuid"]: NodeDefinition(n["name"], n) for n in nodes}
        return nodes

    def robinson_external_sources(self):
        nodes = [n for n in self._nodes().values() if n.is_external_source()]
        nodes = {n["uuid"]: ExternalSourceDefinition(n["name"], n) for n in nodes}
        return nodes

    def robinson_external_sinks(self):
        nodes = [n for n in self._nodes().values() if n.is_external_sink()]
        nodes = {n["uuid"]: ExternalSinkDefinition(n["name"], n) for n in nodes}
        return nodes

    def graph_outputs(self):
        nodes = [n for n in self._nodes().values() if n.is_graph_output()]
        # ipdb.set_trace()
        nodes = {n["uuid"]: GraphOutputDefinition(n["name"], self, n) for n in nodes}
        return nodes

    def graph_inputs(self):
        nodes = [n for n in self._nodes().values() if n.is_graph_input()]
        # ipdb.set_trace()
        nodes = {n["uuid"]: GraphInputDefinition(n["name"], self, n) for n in nodes}
        return nodes

    def compound_nodes(self):
        compounds = [n for n in self._nodes().values() if n.is_compound()]
        compounds = {n["uuid"]: CompositeDefinition(n["name"], n) for n in compounds}
        return compounds

    def compound_nodes_recursive(self):
        compounds = self.compound_nodes()

        for c in compounds.values():
            childs = c.compound_nodes()
            compounds = {**compounds, **childs}

        return compounds

    def computation_nodes(self):
        return {**self.robinson_nodes(), **self.compound_nodes()}

    def nodes(self):
        nodes = self.robinson_nodes()

        external_sources = self.robinson_external_sources()
        external_sinks = self.robinson_external_sinks()

        graph_inputs = self.graph_inputs()
        graph_outputs = self.graph_outputs()

        compounds = self.compound_nodes()

        nodes = {
            **nodes,
            **external_sources,
            **external_sinks,
            **graph_inputs,
            **graph_outputs,
            **compounds,
        }

        return nodes

    def nodes_recursive(self, filter=lambda m: True):
        nodes = self.nodes()

        for c in nodes.values():
            childs = c.nodes()
            nodes = {**nodes, **childs}

        return {k: v for k, v in nodes.items() if filter(v)}

    def config(self):
        if "robinson" in self.data:
            rob = self.data["robinson"]
            if "config" in rob:
                return rob["config"]
        return {}

    def outputs(self):
        if "outputs" in self.data:
            return self.data["outputs"]
        return []

    def inputs(self):
        if "inputs" in self.data:
            return self.data["inputs"]
        return []

    def input_ports(self):
        ports = []
        for p in self.inputs():
            ports.append(InputPortDefinition(p["name"], p))

        return ports

    def output_ports(self):
        ports = []
        for p in self.outputs():
            ports.append(OutputPortDefinition(p["name"], p))

        return ports

    def robinson_def(self):
        if "robinson" in self.data:
            return self.data["robinson"]
        return {}

    def module(self):
        return self.robinson_def()["module"]

    def classname(self):
        return self.robinson_def()["class"]

    def input_portname_by_index(self, idx):
        check_ports = [
            "{0}",
            "dataport_input_{0}",
            "dataport_{0}",
            "eventport_input_{0}",
            "eventport_input",
        ]

        for cp in check_ports:
            try:
                if cp.format(idx) in self.robinson_def()["input_names"]:
                    return cp.format(idx)
            except:
                pass

        raise Exception(f"Could not find portname {idx}")

    def output_portname_by_index(self, idx):

        check_ports = [
            "{0}",
            "dataport_output_{0}",
            "dataport_{0}",
            "eventport_output_{0}",
            "eventport_output",
        ]

        for cp in check_ports:
            try:
                if cp.format(idx) in self.robinson_def()["output_names"]:
                    return cp.format(idx)
            except:
                pass

        raise Exception(f"Could not find portname {idx}")

    def __repr__(self) -> str:
        return f"<Node {self.name()}>"


class ExternalSourceDefinition(NodeDefinition):
    def topic(self):
        return self.data["topic"]

    def input_portname_by_index(self, idx):
        # return f"ExternalSourceInput_{idx}"
        return self.topic()

    def output_portname_by_index(self, idx):
        # return f"ExternalSourceOutput_{idx}"
        return self.topic()

    def name(self):
        return "mqtt"


class ExternalSinkDefinition(NodeDefinition):
    def topic(self):
        return self.data["topic"]

    def input_portname_by_index(self, idx):
        # return f"ExternalSinkInput_{idx}"
        return self.topic()

    def output_portname_by_index(self, idx):
        # return f"ExternalSinkOutput_{idx}"
        return self.topic()

    def name(self):
        return "mqtt"


class GraphInputDefinition(NodeDefinition):
    def __init__(self, name, compound, data) -> None:
        self._name = name
        self.compound = compound
        self.data = data

    def input_portname_by_index(self, idx):
        return f"NOT_IMPLEMENTED_GraphInput_Input_{idx}"

    def output_portname_by_index(self, idx):
        r = [n["name"] for n in self.data["outputs"] if n["pinIndex"] == idx]

        if len(r) > 0:
            return r[0]

        return f"NOT_FOUND_GraphInput_output_{idx}"

    def name(self):
        # ipdb.set_trace()
        # return self.compound.name()
        return super().name()


class GraphOutputDefinition(NodeDefinition):
    def __init__(self, name, compound, data) -> None:
        self._name = name
        self.compound = compound
        self.data = data

    def input_portname_by_index(self, idx):
        # pprint(self.data)
        r = [n["name"] for n in self.data["inputs"] if n["pinIndex"] == idx]

        # ipdb.set_trace()
        if len(r) > 0:
            return r[0]

        return f"GraphOutput_input_{idx}"

    def output_portname_by_index(self, idx):
        # pprint(self.data)
        return f"NOT_IMPLEMENTED_GraphOuput_output_{idx}"

    def name(self):
        return super().name()
        # ipdb.set_trace()
        # return self.compound.name()


class CompositeDefinition(NodeDefinition):
    def __init__(self, name, data):
        self._name = name
        self.data = data

    def __getitem__(self, key):
        # print("__getitem__", key)
        if isinstance(key, int):
            return list(self.data)[key]

        return self.data[key]

    def _nodes(self):
        # ipdb.set_trace()
        if "graphData" in self.data:
            nodes = self.data["graphData"]["nodes"]
            nodes = {n["uuid"]: NodeDefinition(n["name"], n) for n in nodes}
            return nodes
        if "nodes" in self.data:
            nodes = self.data["nodes"]
            nodes = {n["uuid"]: NodeDefinition(n["name"], n) for n in nodes}
            return nodes

    def module(self):
        return "composite_module"

    def classname(self):
        return "CompositeClass"

    def config(self):
        cfg = {}

        for uid, node in self.nodes().items():
            c = node.config()

            if c is None:
                continue

            if len(c) > 0:
                cfg[node.name()] = c

        return cfg

    def input_portname_by_index(self, idx):
        r = [n["name"] for n in self.data["inputs"] if n["pinIndex"] == idx]

        if len(r) > 0:
            return r[0]

        return f"UNKNOWN_{idx}"

    def output_portname_by_index(self, idx):
        r = [n["name"] for n in self.data["outputs"] if n["pinIndex"] == idx]

        if len(r) > 0:
            return r[0]

        return f"UNKNOWN_{idx}"

    def import_modules(self):

        import_modules = {}
        nodes = self.nodes()

        for uuid, n in nodes.items():
            component_name = n["name"]

            try:
                if n.is_robinson():

                    # rob = n.robinson_def()
                    module = n.module()
                    classname = n.classname()
                    fqn = f"{module}.{classname}"

                    # if fqn.lower().find("qt") > 0:
                    # try:
                    #    if issubclass(getattr(importlib.import_module(module), classname), RobinsonQtComponent):
                    #        continue
                    # except Exception as e:
                    #     print("Could not check for RobinsonQtComponent")
                    #     print(e)

                    #     continue
                    import_modules[component_name] = module, classname

                if n.is_compound():
                    # print("Compound Node", n["name"])
                    pass
                if n.is_external():
                    # print("External Node", n["name"])
                    pass
            except Exception as e:
                print("Could not import module ", component_name)
                print(e)
        return import_modules

    def components(self, qt=True):
        import_modules = self.import_modules()

        result = {}

        for name, (module, classname) in import_modules.items():
            if issubclass(
                getattr(importlib.import_module(module), classname), RobinsonQtComponent
            ):
                continue
            result[name] = (module, classname)

        return result

    def connections(self, include_exec=False):
        # nodes = {u:c for u,c in self.nodes().items() if c.is_external() == False}
        nodes = self.nodes()

        components = self.components()

        connections = {}
        for uuid, n in nodes.items():
            out = n.outputs()

            for o in out:
                output_links = o["linkedTo"]
                if len(output_links) == 0:
                    continue
                if include_exec is False:
                    if o["dataType"] == "ExecPin":
                        continue

                for link in output_links:

                    try:
                        from_node = n
                        from_idx = link["outPinId"]
                        # from_name = n["name"]
                        # from_port = rob["output_names"][from_idx - 2]
                        to_uuid = link["rhsNodeUid"]
                        to_idx = link["inPinId"]
                        # try:
                        to_node = nodes[to_uuid]  # if to_uuid in nodes else uuid
                        # print("to_node", to_node)
                        #
                        if from_node.is_external() or to_node.is_external():
                            continue

                        # check if qt components, skiop if true
                        if (
                            from_node._name not in components
                            or to_node._name not in components
                        ):
                            continue

                        key = (from_node, from_idx)

                        if key not in connections:
                            connections[key] = []
                        connections[key].append(
                            CDir(
                                from_node=from_node,
                                from_idx=from_idx,
                                to_node=to_node,
                                to_idx=to_idx,
                            )
                        )
                        # connections.append(
                        #     CDir(
                        #         from_node=from_node,
                        #         from_idx=from_idx,
                        #         to_node=to_node,
                        #         to_idx=to_idx,
                        #     )
                        # )
                    except Exception as e:
                        print(f"Could not connect {n} to {to_uuid}")
                        print(e)

        return connections

    def connections_extern(self):
        # nodes = {u:c for u,c in self.nodes().items() if c.is_external() == False}
        nodes = self.nodes()

        input_connections = {}
        output_connections = {}
        for uuid, n in nodes.items():
            out = n.outputs()

            for o in out:
                output_links = o["linkedTo"]
                if len(output_links) == 0:
                    continue

                for link in output_links:

                    try:
                        from_node = n
                        from_idx = link["outPinId"]
                        # from_name = n["name"]
                        # from_port = rob["output_names"][from_idx - 2]
                        to_uuid = link["rhsNodeUid"]
                        to_idx = link["inPinId"]
                        # try:
                        to_node = nodes[to_uuid]  # if to_uuid in nodes else uuid
                        # print("to_node", to_node)
                        #
                        if (
                            from_node.is_external() == False
                            and to_node.is_external() == False
                        ):
                            continue

                        if from_node.is_external():
                            key = (from_node, from_idx)

                            if key not in input_connections:
                                input_connections[key] = []
                            input_connections[key].append(
                                CDir(
                                    from_node=from_node,
                                    from_idx=from_idx,
                                    to_node=to_node,
                                    to_idx=to_idx,
                                )
                            )
                        if to_node.is_external():
                            key = (to_node, to_idx)

                            if key not in output_connections:
                                output_connections[key] = []
                            output_connections[key].append(
                                CDir(
                                    from_node=from_node,
                                    from_idx=from_idx,
                                    to_node=to_node,
                                    to_idx=to_idx,
                                )
                            )

                    except Exception as e:
                        print(f"Could not connect {n} to {to_uuid}")
                        print(e)
        return input_connections, output_connections

    def connections_extern_input(self):
        return self.connections_extern()[0]

    def connections_extern_output(self):
        return self.connections_extern()[1]
