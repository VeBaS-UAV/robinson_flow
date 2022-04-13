#!/usr/bin/env python3

from dynaconf import Dynaconf

def _get_config_files():
    return ['settings.toml']

settings = Dynaconf(
    environments=True,
    envvar_prefix="ROBINSON_FLOW",
    env_switcher="ROBINSON_FLOW_MODE",
    # root_path="/home/matthias/src/robinson/robinson_flow/robinson_flow",
    settings_files=_get_config_files(),
)
