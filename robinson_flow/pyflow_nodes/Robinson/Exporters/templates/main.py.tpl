from robinson.components import Composite
from robinson.components import ComponentRunner

from robinson_flow.connector import ExternalConnectionHandler
from robinson.components import DataPortOutput, DataPort, DataPortInput, ComponentRunner

<%include file="components_import.py.tpl"/> \

<%include file="config_init.py.tpl"/> \




class ${base.name().title().replace(".","")|pyname}(Composite):

    def __init__(self, name:str):
        super().__init__(name)

## % for name, (module, classname) in base.import_modules().items():
% for name, (module, classname) in base.components().items():
        self.${name.lower()} = ${name}('${name.lower()}')
% endfor

% for name, (module, classname) in base.components().items():
        self.add(self.${name.lower()})
% endfor

% for from_tuple, cons in base.connections().items():
% for c in cons:
        self.${c.from_name().lower()|pyname}.${c.from_port()|pyname}.connect(self.${c.to_name().lower()|pyname}.${c.to_port()|pyname})
% endfor
% endfor

        # defining composite ports
% for key_tuple, cons in base.connections_extern_input().items():
        self.dataport_input_${key_tuple[0].topic().lower()|pyname} = DataPortInput("${key_tuple[0].topic()|pyname}")
% for c in cons:
        self.dataport_input_${key_tuple[1].lower()|pyname} += self.${c.to_name().lower()|pyname}.${c.to_port()|pyname}
% endfor

% endfor
        # #####
% for key_tuple, cons in base.connections_extern_output().items():
        self.dataport_output_${key_tuple[0].topic().lower()|pyname} = DataPortOutput("${key_tuple[0]._name.lower()|pyname}_${from_tuple[1]|pyname}")
% for c in cons:
        self.${c.from_name().lower()|pyname}.${c.from_port()|pyname} += self.dataport_output_${key_tuple[0].topic().lower()|pyname}
% endfor

% endfor
        # #####

def init_external_connections(composite, external):
% for from_tuple, cons in base.connections_extern_input().items():
% for c in cons:
    external.external_source("${c.from_node.topic()}").connect(\
\
composite.dataport_input_${c.from_node.topic().lower()|pyname})
% endfor
% endfor

% for to_tuple, cons in base.connections_extern_output().items():
% for c in cons:
    composite.dataport_output_${c.to_port()|pyname}.connect(\
external.external_sink("${to_tuple[0].topic()}"))
% endfor
% endfor


if __name__ == "__main__":
    runner = ComponentRunner('runner')

    external = ExternalConnectionHandler.instance()
    composite = ${base.name().title().replace(".","")|pyname}("${base.name().title().replace('.','_')}")

    init_external_connections(composite, external)

    runner += external
    runner += composite

    composite.config_update(**settings["components"])

    runner.run()
