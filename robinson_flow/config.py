#!/usr/bin/env python3

from dynaconf import Dynaconf
import pathlib

import logging
import logging.config

import robinson_flow
from pprint import pprint

_config_log = False

def dynaconf_config_files():
    cfg_dir = (pathlib.Path(robinson_flow.__file__).parent.parent / "config")# / "logging.ini")
    pprint(cfg_dir)

    cfg_files =  [str((cfg_dir/f)) for f in ["settings.yaml", "settings.environment.yaml", ".secrets.yaml", "logging.yaml"]]

    pprint(cfg_files)
    return cfg_files

_settings = Dynaconf(
    environments=True,
    envvar_prefix="ROBINSON_FLOW",
    env_switcher="ROBINSON_FLOW_MODE",
    settings_files=dynaconf_config_files()
)

def default_config():
    global _config_log
    global _settings

    if _config_log is False:
        pprint("Current config:")
        pprint(_settings.as_dict())
        _config_log = True

    return _settings
# print("Settings")
# pprint(settings.as_dict())
