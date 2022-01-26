% for name, (module, classname) in base.import_modules().items():
from ${module} import ${classname} as ${name}
% endfor
