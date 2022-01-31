% for name, (module, classname) in base.import_modules().items():
${name.lower()} = ${name}('${name.lower()}')
% endfor
