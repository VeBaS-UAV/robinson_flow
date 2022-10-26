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

% for c in base.connections():
        self.${c.from_name().lower()|pyname}.${c.from_port()|pyname}.connect(self.${c.to_name().lower()|pyname}.${c.to_port()|pyname})
% endfor

        #defining composite ports
% for c in base.connections_extern():
% if c.from_node.is_external():
        self.dataport_input_${c.from_port()|pyname} = self.${c.to_name().lower()|pyname}.${c.to_port()|pyname}
% endif
% if c.to_node.is_external():
        self.dataport_output_${c.to_port()|pyname} = self.${c.from_name().lower()|pyname}.${c.from_port().lower()|pyname}
% endif
% endfor

def init_external_connections(composite, external):
% for c in base.connections_extern():
% if c.from_node.is_external():
    external.external_source("${c.from_node.topic()}").connect(\
% else:
    composite.dataport_output_${c.to_port()|pyname}.connect(\
% endif
\
% if c.to_node.is_external():
external.external_sink("${c.to_node.topic()}"))
% else:
composite.dataport_input_${c.from_port()|pyname})
% endif
% endfor

<%doc>
% for c in base.compound_nodes_recursive().values():
<%include file="composite_class.py.tpl" args="composite=c"/>
% endfor
\
% for c in base.compound_nodes_recursive().values():
<%include file="composite_init.py.tpl" args="composite=c"/>
% endfor
\
<%include file="components_init.py.tpl"/> \

<%include file="environment_init.py.tpl"/> \

<%include file="connections_init.py.tpl"/> \

<%include file="runner_init.py.tpl"/> \

<%include file="runner_start.py.tpl"/>
</%doc>

if __name__ == "__main__":
    runner = ComponentRunner('runner')

    external = ExternalConnectionHandler.instance()
    composite = ${base.name().title().replace(".","")|pyname}("${base.name().title().replace('.','_')}")

    init_external_connections(composite, external)

    runner += external
    runner += composite

    composite.config_update(**settings["components"])

    runner.run()
