% for name, (module, classname) in base.import_modules().items():
from ${module} import ${classname} as ${name}
% endfor

% for c in base.compound_nodes_recursive().values():
% for name, (module, classname) in c.import_modules().items():
from ${module} import ${classname} as ${name}
% endfor
% endfor
