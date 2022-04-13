#!/usr/bin/env python3

from dynaconf import Dynaconf
import pathlib

import robinson_flow
from pprint import pprint

def dynaconf_config_files():
    cfg_dir = (pathlib.Path(robinson_flow.__file__).parent.parent / "config")# / "logging.ini")
    pprint(cfg_dir)

    cfg_files =  [str((cfg_dir/f)) for f in ["settings.yaml", "settings.environment.yaml", ".secrets.yaml", "logging.yaml"]]

    pprint(cfg_files)
    return cfg_files

settings = Dynaconf(
    environments=True,
    envvar_prefix="ROBINSON_FLOW",
    env_switcher="ROBINSON_FLOW_MODE",
    settings_files=dynaconf_config_files()
)

# print("Settings")
# pprint(settings.as_dict())
