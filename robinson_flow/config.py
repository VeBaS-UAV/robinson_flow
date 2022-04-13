#!/usr/bin/env python3

from dynaconf import Dynaconf

def _get_config_files():
    return ['settings.yaml']

settings = Dynaconf(
    environments=True,
    envvar_prefix="ROBINSON_FLOW",
    env_switcher="ROBINSON_FLOW_MODE",
    settings_files=_get_config_files(),
)
