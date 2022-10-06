#!/usr/bin/env python3

from dynaconf import Dynaconf
import pathlib

import logging
import logging.config

from yaml import events

import robinson_flow
from pprint import pprint

_config_log = True

import __main__ as main

_logging_config_done = False

_additional_config_files = []
_dynamic_config_files = []


def dynaconf_config_files():
    exec_cfg_file = pathlib.Path(main.__file__).with_suffix(".yaml")
    #
    # cfg_dir = (pathlib.Path(robinson_flow.__file__).parent.parent / "config")# / "logging.ini")
    # pprint(cfg_dir)

    # cfg_files_names = ["settings.yaml", "settings.environment.yaml", ".secrets.yaml", "logging.yaml"]

    # cfg_files =  [str((cfg_dir/f)) for f in cfg_files_names]
    cfg_files = []

    cfg_files += _additional_config_files
    cfg_files += _dynamic_config_files
    cfg_files.append(exec_cfg_file)
    cfg_files.append(exec_cfg_file.with_suffix(".env.yaml"))
    cfg_files.append(exec_cfg_file.with_suffix(".local.yaml"))

    pprint(cfg_files)

    return cfg_files


def add_config(config_file):
    _additional_config_files.append(config_file)


def merge_config(config_file):
    _dynamic_config_files.clear()
    _dynamic_config_files.append(config_file)


def current():
    global _logging_config_done

    _settings = Dynaconf(
        environments=True,
        envvar_prefix="ROBINSON_FLOW",
        env_switcher="ROBINSON_FLOW_MODE",
        settings_files=dynaconf_config_files(),
    )

    dynsetting = Dynaconf(settings_files=_dynamic_config_files)
    print("DynSetting")
    pprint(dynsetting.as_dict())
    print("Settings")
    pprint(_settings.as_dict())

    if _logging_config_done is False:
        try:
            logging.config.dictConfig(_settings.logging)
        except:
            pass

            logging.getLogger("vebas").setLevel(logging.DEBUG)
            logging.getLogger("robinson.messaging").setLevel(logging.INFO)
            logging.getLogger("robinson.components").setLevel(logging.INFO)
        _logging_config_done = True

    return _settings
