#!/usr/bin/env python3

import inspect
import pydantic

class RobinsonWrapperMixin():
    input_name = "dataport_input"
    output_name = "dataport_output"

    def create_component(self):
        self.logger.info(f"Creating component {self.cls} for node {self.name}")
        try:
                self.component = self.cls(self.name)
        except Exception as e:
                self.logger.error(f"error while setting up component {self.cls}")
                self.logger.error(e)
                self.component = None

    def cl_input_ports(self, cl):
        ports = [f for f in dir(cl) if f.startswith(self.input_name)]
        return [(name, getattr(cl, name)) for name in ports]

    def cl_output_ports(self, cl):
        ports = [f for f in dir(cl) if f.startswith(self.output_name)]
        return [(name, getattr(cl, name)) for name in ports]

    def extract_output_name(self, port_name):
        base_name = port_name[len(self.output_name)+1:]
        if len(base_name) == 0:
            return "output"
        return base_name

    def extract_input_name(self, port_name):
        base_name = port_name[len(self.input_name)+1:]
        if len(base_name) == 0:
            return "input"
        return base_name

    def extract_init_items(self, cls):
        init_parameters = inspect.signature(cls.init).parameters

        if init_parameters is not None:
            return [(name, p.annotation) for (name, p) in init_parameters.items() if name != "self"]

        return []

    def extract_config_items(self, cls):
        try:
            if (isinstance(cls.config, pydantic.BaseModel)):
                return [(name, cls.config.__fields__[name].type_) for (name, _) in cls.config.__dict__.items()]
            else:
                cfg_parameter = inspect.signature(cls.config).parameters
                return [(name, p.annotation) for (name, p) in cfg_parameter.items() if name != "self"]
        except Exception as e:
            print("Error in extract_config_item")
            print(e)
            return []

    def call_input_port_by_name(self, name, *args, **kw_args):
        # print("call_input_port_by_name", name, args, kw_args)
        func = getattr(self.component, name)

        # if name == "dataport_input_marker":
        #     pass

        # if name == "dataport_input_args":
        #     pass
        try:
            sig = inspect.signature(func)
            param = sig.parameters
            # print("sig", sig, param, param.items())
            if len(param.items()) == 0:
                func()
            if len(param.items()) == 1:
                func(*args, **kw_args)
            elif len(param.items()) > 1:
                if len(args) > 1:
                    func(*args, **kw_args)
                else:
                    if isinstance(args[0], set):
                        func(*args[0])
                    elif isinstance(args[0], tuple):
                        func(*args[0])
                    elif isinstance(args[0], dict):
                        func(**args[0])
        except Exception as e:
            self.logger.error(f"Could not call input porty {self.cls}.{name}")
            self.logger.error(e)

    def call_output_port_by_index(self, index, *args, **kw_args):
        # print("call outputport by index", index, args, kw_args)
        if len(args) == 1:
            self.outputs[index].set_val(args[0])
        else:
            self.outputs[index].set_val(args)

    def update_init(self, key, value):
        self.logger.info(f"update_init {key}:{value}")
        self.init_args[key] = value

        try:
            self.component.init(**self.init_args)
        except Exception as e:
            self.logger.warn(f"Could not init config")
            self.logger.error(e)

    def update_config(self, key, value):
        self.logger.info(f"update_init {key}:{value}")
        self.config_args[key] = value

        try:
            self.component.config_update(**self.config_args)
        except Exception as e:
            self.logger.warn(f"Could not init config")
            self.logger.error(e)
