#!/usr/bin/env python3

import json
import yaml
import pickle

from typing import List
# json.load(open("graph_export_test.py"), strict=False)
# with open("graph_export_test.py", "rb") as read_file:
   # data = json.load(read_file, strict=False)

# data = pickle.load(open("/home/matthias/src/pyflow/PyFlow/graph_export.pickle"))

data = yaml.load(open("/home/matthias/src/pyflow/PyFlow/graph_export.yaml"), Loader=yaml.CLoader)

# %%

class CompositeDefinition():

    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.import_modules = {}
        self.components_init = {}

    def nodes(self):
        nodes = [n for n in data["nodes"] if "robinson" in n]
        nodes = {n["uuid"]:n for n in nodes}
        return nodes

    def update_codelines(self):

        for uuid,n in self.nodes.items():

                component_name = n["name"]
                rob = n["robinson"]
                module = rob["module"]
                classname = rob["class"]
                fqn = f"{module}.{classname}"

                self.import_modules[component_name] = module, classname
                self.components_init[component_name] = module, classname

# %%

components = [n for n in data["nodes"] if "graphData" in n]
components


# %%


# %%
from pydantic import BaseModel

class CDir(BaseModel):
    from_node:dict = None
    from_idx:int = None
    to_node:dict = None
    to_idx:int = None


    def from_name(self):
        return self.from_node["name"]
    def to_name(self):
        return self.to_node["name"]

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


n1["outputs"][0]["linkedTo"]
n1["outputs"]

connections:List[CDir] = []

for uuid,n in nodes.items():
    out = n["outputs"]
    rob = n["robinson"]
    output_portnames = n["robinson"]["output_names"]

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
            to_node = nodes[to_uuid]
            to_name = to_node["name"]

            if "robinson" in to_node:
                # to_port = n_to["robinson"]["input_names"][to_idx-2]

                connections.append(CDir(from_node=from_node, from_idx=from_idx, to_node=to_node, to_idx=to_idx))

            else:
                print("Could not identify node {to_name}")
connections
# %%
#
from io import StringIO
buf = StringIO()

buf.write("#!/usr/bin/env python3\n")
buf.write("\n")
buf.write("from robinson.components import ComponentRunner\n")
buf.write("\n")

for name, (module, classname) in import_modules.items():
   buf.write(f"from {module} import {classname} as {name}_component\n")

buf.write("\n")
for name, (module, classname) in components_init.items():
   buf.write(f"{name} = {name}_component('{name}')\n")

buf.write("\n")

for c in connections:

    buf.write(f"{c.from_name()}.{c.from_port()}.connect({c.to_name()}.{c.to_port()})\n")


buf.write("\n")
buf.write("\n")

buf.write("runner = ComponentRunner('runner')\n")
for name, fqn in components_init.items():
   buf.write(f"runner += {name}\n")

buf.write("\n")
buf.write(f"runner.run()\n")
print(buf.getvalue())

with open('testrun.py', mode='w') as f:
    print(buf.getvalue(), file=f)
