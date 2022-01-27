runner = ComponentRunner('runner')

% for name, (module, classname) in base.import_modules().items():
runner += ${name.lower()}
% endfor
