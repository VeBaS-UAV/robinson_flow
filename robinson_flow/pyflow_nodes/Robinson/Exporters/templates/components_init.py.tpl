% for name, (module, classname) in base.import_modules().items():
        self.${name.lower()} = ${name}("{name.lower()}")
% endfor
