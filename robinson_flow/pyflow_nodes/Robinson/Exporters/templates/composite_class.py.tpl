<%page args="composite"/>
class ${composite.name().capitalize()|pyname}_Composite(Composite):

    def __init__(self, name):
        super().__init__(name)
\
        % for uuid, child in composite.computation_nodes().items():
        <%
            var_name = child.name().lower()
            class_name = child.name()
        %>
        self.${var_name|pyname} = ${class_name|pyname}('${var_name}')\
        % endfor

        % for port in composite.output_ports():
        <%
            name = port.name
        %>
        self.${name} = DataPortOutput('${name}')\
        % endfor

        % for port in composite.input_ports():
        <%
        name = port.name
        %>
        self.${name} = DataPort('${name}')\
        % endfor

        % for c in composite.connections():
        <%
            from_component = f"self.{c.from_name().lower()}"
            if c.from_node.is_graph_port():
               from_component = "self"
            from_port = c.from_port()
            from_statement = f"{from_component}.{from_port}"

            to_component = f"self.{c.to_name().lower()}"
            if c.to_node.is_graph_port():
               to_component = "self"
            to_port = c.to_port()
            to_statement = f"{to_component}.{to_port}"
        %>
        ${from_statement}.connect(${to_statement})\
        % endfor

% for name, (module, classname) in composite.import_modules().items():
        self += self.${name.lower()}
% endfor
