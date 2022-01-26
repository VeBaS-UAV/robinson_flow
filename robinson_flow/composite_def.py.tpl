class ${base.name().capitalize()}Composite(Composite):

% for uuid, child in base.computation_nodes().items():
<%
    var_name = child["name"].lower()
    class_name = child["name"]
%> \
    ${var_name} = ${class_name}('${var_name}')
% endfor

% for port in base.output_ports():
<%
        name = port.name
%> \
    dataport_output_${name} = DataPortOutput('${name}')
% endfor

% for port in base.input_ports():
<%
    name = port.name
%> \
    dataport_input_${name} = DataPort('${name}')
% endfor
