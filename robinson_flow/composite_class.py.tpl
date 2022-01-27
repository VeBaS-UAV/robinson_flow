${base}
class ${base.name().capitalize()}Composite(Composite):

% for uuid, child in base.computation_nodes().items():
<%
    var_name = child["name"].lower()
    class_name = child["name"]
%>\
    ${var_name} = ${class_name}('${var_name}')
% endfor
\
% for port in base.output_ports():
<%
    name = port.name
%>\
    ${name} = DataPortOutput('${name}')
% endfor
\
% for port in base.input_ports():
<%
    name = port.name
%>\
    ${name} = DataPort('${name}')
% endfor

    def __init__(self, name):
        super(Composite).__init__(name)

        % for c in base.connections():
        <%
            from_component = c.from_name().lower()
            if c.from_node.is_graph_port():
               from_component = "self"
            from_port = c.from_port()
            from_statement = f"{from_component}.{from_port}"

            to_component = c.to_name().lower()
            if c.to_node.is_graph_port():
               to_component = "self"
            to_port = c.to_port()
            to_statement = f"{to_component}.{to_port}"
        %>
        ${from_statement}.connect(${to_statement})
        % endfor

% for name, (module, classname) in base.import_modules().items():
        self += self.${name.lower()}
% endfor
