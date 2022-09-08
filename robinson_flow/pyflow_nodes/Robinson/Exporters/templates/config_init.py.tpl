from dynaconf import Dynaconf

import pathlib

def _get_config_files():
    cfg_file = pathlib.Path(__file__).with_suffix(".yaml")
    return [cfg_file, "env.yaml"]

settings = Dynaconf(
    envvar_prefix="ROBINSON_FLOW",
    settings_files=_get_config_files(),
)
