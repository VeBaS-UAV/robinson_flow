#!/usr/bin/env python3

import json
import yaml
import pickle

from pydantic import BaseModel
from typing import Any, List


class CDir(BaseModel):
    from_node:Any = None
    from_idx:int = None
    to_node:Any = None
    to_idx:int = None


    def from_name(self):
        try:
            return self.from_node["name"]
        except Exception as e:
            print(e, self.from_node)
            return "ERROR_from_name"

    def to_name(self):
        try:
            return self.to_node["name"]
        except Exception as e:
            print(e, self.to_node)
            return "ERROR_to_name"

    def from_port(self):
        try:
            return self.from_node["robinson"]["output_names"][self.from_idx - 2]
        except Exception as e:
            print(e, self.to_idx)
            return "ERROR"

    def to_port(self):
        try:
            return self.to_node["robinson"]["input_names"][self.to_idx - 2]
        except Exception as e:
            print(e, self.to_idx)
            return "ERROR"


    def __repr__(self):
        return f"Connection({self.from_name()}.{self.from_port()} -> {self.to_name()}.{self.to_port()})"


    # json.load(open("graph_export_test.py"), strict=False)
# with open("graph_export_test.py", "rb") as read_file:
   # data = json.load(read_file, strict=False)

# data = pickle.load(open("/home/matthias/src/pyflow/PyFlow/graph_export.pickle"))

data = yaml.load(open("/home/matthias/src/pyflow/PyFlow/graph_export.yaml"), Loader=yaml.CLoader)

# %%
class NodeDefinition():

    def __init__(self, name, data) -> None:
        self.name = name
        self.data = data

    def __getitem__(self, key):
        # print("__getitem__", key)
        if isinstance(key, int):
            return list(self.data)[key]

        return self.data[key]

    def outputs(self):
        if "outputs" in self.data:
            return self.data["outputs"]
        return []

    def inputs(self):
        if "inputs" in self.data:
            return self.data["inputs"]
        return []

    def robinson_def(self):
        if "robinson" in self.data:
            return self.data["robinson"]
        return {}

    def module(self):
        return self.robinson_def()["module"]

    def classname(self):
        return self.robinson_def()["class"]


class CompositeDefinition(NodeDefinition):

    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.import_modules = {}
        self.components_init = {}
        self.connections:List[CDir] = []

    def __getitem__(self, key):
        # print("__getitem__", key)
        if isinstance(key, int):
            return list(self.data)[key]

        return self.data[key]

    def module(self):
        return "composite_module"

    def classname(self):
        return "CompositeClass"

    def export_to_python(self):

        from io import StringIO
        buf = StringIO()

        buf.write("#!/usr/bin/env python3\n")
        buf.write("\n")
        buf.write("from robinson.components import ComponentRunner\n")
        buf.write("\n")

        for name, (module, classname) in self.import_modules.items():
            buf.write(f"from {module} import {classname} as {name}_component\n")

        buf.write("\n")
        for name, (module, classname) in self.components_init.items():
            buf.write(f"{name} = {name}_component('{name}')\n")

        buf.write("\n")

        for c in self.connections:
            buf.write(f"{c.from_name()}.{c.from_port()}.connect({c.to_name()}.{c.to_port()})\n")


        buf.write("\n")
        buf.write("\n")

        buf.write("runner = ComponentRunner('runner')\n")
        for name, fqn in self.components_init.items():
            buf.write(f"runner += {name}\n")

        buf.write("\n")
        buf.write(f"runner.run()\n")
        print(buf.getvalue())

        # with open('testrun.py', mode='w') as f:
            # print(buf.getvalue(), file=f)

    def robinson_nodes(self):
        nodes = [n for n in self.data["nodes"] if self.is_robinson(n)]
        nodes = {n["uuid"]:NodeDefinition(n['name'],n) for n in nodes}


        return nodes

    def compound_nodes(self):
        compounds = [n for n in self.data["nodes"] if self.is_compound(n)]
        compounds = {n["uuid"]:n for n in compounds}
        return compounds

    def nodes(self):
        nodes = self.robinson_nodes()

        compounds = self.compound_nodes()
        for uuid, c in compounds.items():
            # print(c["name"])
            sub = CompositeDefinition(c["name"],c["graphData"])

            nodes = {**nodes,**{uuid:sub}}

        return nodes

    def is_robinson(self,n):
        return "robinson" in n

    def is_compound(self, n):
        return "graphData" in n

    def update_codelines(self):

        self.import_modules = {}
        self.components_init = {}
        self.connections:List[CDir] = []

        nodes = self.nodes()

        for uuid,n in nodes.items():
            component_name = n["name"]

            if self.is_robinson(n):
                # rob = n.robinson_def()
                module = n.module()
                classname = n.classname()
                fqn = f"{module}.{classname}"

                self.import_modules[component_name] = module, classname
                self.components_init[component_name] = module, classname

            if self.is_compound(n):
                print("Compound Node", n["name"])
                pass

        for uuid,n in nodes.items():
            out = n.outputs()

            for o in out:
                output_links = o["linkedTo"]
                if len(output_links) == 0:
                    continue

                for link in output_links:
                    # print(n["name"], link)

                    from_node = n
                    from_idx = link["outPinId"]
                    # from_name = n["name"]
                    # from_port = rob["output_names"][from_idx - 2]
                    to_uuid = link["rhsNodeUid"]
                    to_idx = link['inPinId']
                    try:
                        to_node = nodes[to_uuid]
                    except:
                        to_node = to_uuid
                    self.connections.append(CDir(from_node=from_node, from_idx=from_idx, to_node=to_node, to_idx=to_idx))
                    # if "robinson" in to_node:
                        # to_port = n_to["robinson"]["input_names"][to_idx-2]
                    # else:
                        # print("Could not identify node {to_name}")



cd = CompositeDefinition("test",data)

[print(uid,n["name"]) for uid, n in cd.robinson_nodes().items()]
[print(uid,n["name"]) for uid, n in cd.compound_nodes().items()]
[print(uid,n["name"]) for uid, n in cd.nodes().items()]

# cd.update_codelines()
c = list(cd.compound_nodes().items())[0][1]
c["name"]
c["graphData"]

cd.update_codelines()

cd.connections

cd.export_to_python()

ccd = CompositeDefinition("comp", c["graphData"])

ccd.robinson_nodes()
[print(uid,n["name"]) for uid, n in ccd.robinson_nodes().items()]
[print(uid,n["name"]) for uid, n in ccd.compound_nodes().items()]
[print(uid,n["name"]) for uid, n in ccd.nodes().items()]

# c["graphData"]["nodes"]
ccd.nodes()
ccd.update_codelines()
ccd.export_to_python()

# %%
#
components = [n for n in data["nodes"] if "graphData" in n]
components

c["outputs"]
