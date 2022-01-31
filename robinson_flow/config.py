#!/usr/bin/env python3

from dynaconf import Dynaconf

def _get_config_files():

    return ['settings.toml', '.secrets.toml']

settings = Dynaconf(
    envvar_prefix="ROBINSON_FLOW",
    root_path="/home/matthias/src/robinson/robinson_flow",
    settings_files=_get_config_files(),
)
