external = ExternalConnectionHandler()

% for c in base.connections():
${c.from_name().lower()}.${c.from_port()}.connect(${c.to_name().lower()}.${c.to_port()})
% endfor

% for c in base.connections_extern():
% if c.from_node.is_external():
external.external_source("${c.from_node.topic()}").connect(\
% else:
${c.from_name().lower()}.${c.from_port()}.connect(\
% endif
\
% if c.to_node.is_external():
external.external_sink("${c.to_node.topic()}"))
% else:
${c.to_name().lower()}.${c.to_port()})
% endif
% endfor
