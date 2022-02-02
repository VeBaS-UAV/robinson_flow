% for c in base.connections():
${c.from_name().lower()|pyname}.${c.from_port()|pyname}.connect(${c.to_name().lower()|pyname}.${c.to_port()|pyname})
% endfor
\
% for c in base.connections_extern():
% if c.from_node.is_external():
external.external_source("${c.from_node.topic()|pyname}").connect(\
% else:
${c.from_name().lower()|pyname}.${c.from_port()|pyname}.connect(\
% endif
\
% if c.to_node.is_external():
external.external_sink("${c.to_node.topic()|pyname}"))
% else:
${c.to_name().lower()|pyname}.${c.to_port()|pyname})
% endif
% endfor
