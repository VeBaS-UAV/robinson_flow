#!/usr/bin/env python3

from dynaconf import Dynaconf
import pathlib

import logging
import logging.config

from yaml import events

import robinson_flow
from pprint import pprint

_config_log = True


_dynamic_config_files = []
def dynaconf_config_files():
    cfg_dir = (pathlib.Path(robinson_flow.__file__).parent.parent / "config")# / "logging.ini")
    # pprint(cfg_dir)

    cfg_files_names = ["settings.yaml", "settings.environment.yaml", ".secrets.yaml", "logging.yaml"]

    cfg_files =  [str((cfg_dir/f)) for f in cfg_files_names]

    cfg_files += _dynamic_config_files
    pprint(cfg_files)

    return cfg_files


def merge_config(config_file):
    _dynamic_config_files.clear()
    _dynamic_config_files.append(config_file)

def current():
    _settings = Dynaconf(

    envvar_prefix="ROBINSON_FLOW",
    env_switcher="ROBINSON_FLOW_MODE",
    settings_files=dynaconf_config_files()
    )

    dynsetting = Dynaconf(settings_files=_dynamic_config_files)
    print("DynSetting")
    pprint(dynsetting.as_dict())
    print("Settings")
    pprint(_settings.as_dict())

    return _settings
