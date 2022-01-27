<%include file="components_import.py.tpl"/>

from robinson.components import Composite

% for c in base.compound_nodes_recursive().values():
${c}
<%include file="composite_class.py.tpl" kwargs="base='${c}'"/>
% endfor

<%include file="composite_init.py.tpl"/>

<%include file="components_init.py.tpl"/>


<%include file="connections_init.py.tpl"/>
