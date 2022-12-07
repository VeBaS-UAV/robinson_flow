#!/usr/bin/env python3

from functools import partial
import importlib
import inspect

import pydantic

# TODO build some kind of proxy for robinson components for easy reloading
class RobinsonWrapperMixin:
    input_name = "dataport_input"
    output_name = "dataport_output"
    eventinput_name = "eventport_input"
    eventoutput_name = "eventport_output"

    def create_component(self):

        self.logger.info(f"Creating component {self.cls} for node {self.name}")

        # check if component has been initialized before -> clean up
        if hasattr(self, "component"):
            if self.component is not None:
                self.component.cleanup()

        # reload module for hot updates
        module = importlib.import_module(self.cls.__module__)
        importlib.reload(module)
        self.cls = [
            c[1] for c in inspect.getmembers(module) if c[0] == self.cls.__name__
        ][0]

        try:
            self.component = self.cls(self.name)
            self.register_generic_callback()

            self.component.init()
        except Exception as e:
            self.logger.error(f"error while setting up component {self.cls}")
            self.logger.error(e)
            self.component = None

    def generic_output_callback(self, name, *args, **kwargs):
        self.logger.warn(
            "generic output callback called %s, %s, %s", name, args, kwargs
        )

    def register_generic_callback(self):
        input_ports = self.cl_input_ports(self.component)
        output_ports = self.cl_output_ports(self.component)
        eventinput_ports = self.cl_event_input_ports(self.component)
        eventoutput_ports = self.cl_event_output_ports(self.component)

        for name, port_callable in output_ports:
            port_callable.connect(partial(self.generic_output_callback, name))
        for name, port_callable in eventoutput_ports:
            port_callable.connect(partial(self.generic_output_callback, name))

    def cl_input_ports(self, cl):
        ports = [f for f in dir(cl) if f.startswith(self.input_name)]
        return [(name, getattr(cl, name)) for name in ports]

    def cl_output_ports(self, cl):
        ports = [f for f in dir(cl) if f.startswith(self.output_name)]
        return [(name, getattr(cl, name)) for name in ports]

    def cl_event_input_ports(self, cl):
        ports = [f for f in dir(cl) if f.startswith(self.eventinput_name)]
        return [(name, getattr(cl, name)) for name in ports]

    def cl_event_output_ports(self, cl):
        ports = [f for f in dir(cl) if f.startswith(self.eventoutput_name)]
        return [(name, getattr(cl, name)) for name in ports]

    def extract_output_name(self, port_name):
        base_name = port_name[len(self.output_name) + 1 :]
        if len(base_name) == 0:
            return "output"
        return base_name

    def extract_input_name(self, port_name):
        base_name = port_name[len(self.input_name) + 1 :]
        if len(base_name) == 0:
            return "input"
        return base_name

    def extract_eventoutput_name(self, port_name):
        base_name = port_name[len(self.eventoutput_name) + 1 :]
        if len(base_name) == 0:
            return "eventoutput"
        return base_name

    def extract_eventinput_name(self, port_name):
        base_name = port_name[len(self.eventinput_name) + 1 :]
        if len(base_name) == 0:
            return "eventinput"
        return base_name

    def extract_init_items(self, cls):
        init_parameters = inspect.signature(cls.init).parameters

        if init_parameters is not None:
            return [
                (name, p.annotation)
                for (name, p) in init_parameters.items()
                if name != "self"
            ]

        return []

    def extract_config_items(self, cls):
        try:
            if isinstance(cls.config, pydantic.BaseModel):
                return [
                    (name, cls.config.__fields__[name].type_)
                    for (name, _) in cls.config.__dict__.items()
                ]
            else:
                cfg_parameter = inspect.signature(cls.config).parameters
                return [
                    (name, p.annotation)
                    for (name, p) in cfg_parameter.items()
                    if name != "self"
                ]
        except Exception as e:
            self.logger.info(f"Error in extract_config_item: {e}")
            return []

    def get_callable_by_portname(self, name):
        func = getattr(self.component, name)
        return func

    def call_port_by_name(self, name, *args, **kw_args):
        func = self.get_callable_by_portname(name)

        try:
            sig = inspect.signature(func)
            param = sig.parameters
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
                    else:
                        func(args[0])
        except Exception as e:
            self.logger.error(f"Could not call input port {self.cls}.{name}: {e}")

    def update_init(self, key, value):
        self.logger.info(f"update_init {key}:{value}")
        self.init_args[key] = value

        try:
            self.component.init(**self.init_args)
        except Exception as e:
            self.logger.error(f"Could not init config: {e}")

    def update_config(self, key, value):
        self.logger.info(f"update_init {key}:{value}")
        self.config_args[key] = value

        try:
            self.component.config_update(**self.config_args)
        except Exception as e:
            self.logger.error(f"Could not init config: {e}")
