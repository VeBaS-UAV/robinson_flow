from robinson.components import Composite
from robinson.components import ComponentRunner

from robinson_flow.connector import ExternalConnectionHandler
from robinson.components import DataPortOutput, DataPort, DataPortInput
from robinson.components.qt import QtComponentRunner

<%include file="components_import.py.tpl"/> \

<%include file="config_init.py.tpl"/> \

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
