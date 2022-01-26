% for c in base.connections():
${c.from_name().lower()}.${c.from_port()}.connect(${c.to_name().lower()}.${c.to_port()})
% endfor
