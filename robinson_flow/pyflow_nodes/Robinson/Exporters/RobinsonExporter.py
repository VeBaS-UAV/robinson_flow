import logging
import traceback
from datetime import datetime
from typing import OrderedDict
from PyFlow.UI.UIInterfaces import IDataExporter
from PyFlow.Core.version import Version

import black

from io import StringIO
from mako.lookup import TemplateLookup
import pathlib
import inspect

import re
import yaml
from pprint import pprint
import robinson.config

from robinson_flow.pyflow_nodes.Robinson.Exporters.parser_classes import (
    CompositeDefinition,
)


def pyname(name):
    base_str = name.replace("-", "_").replace("/", "_").replace("__", "_")

    base_str = re.sub("^_", "", base_str)

    return base_str


class RobinsonExporter(IDataExporter):
    """docstring for DemoExporter."""

    def __init__(self):
        super(RobinsonExporter, self).__init__()

    @staticmethod
    def createImporterMenu():
        return False

    @staticmethod
    def creationDateString():
        return datetime.now().strftime("%I:%M%p on %B %d, %Y")

    @staticmethod
    def version():
        return Version(1, 0, 0)

    @staticmethod
    def toolTip():
        return "Robinson Export/Import."

    @staticmethod
    def displayName():
        return "Robinson exporter"

    @staticmethod
    def doImport(pyFlowInstance):
        pass

    @staticmethod
    def doExport(instance):
        pyname_filter = "from robinson_flow.pyflow_nodes.Robinson.Exporters.RobinsonExporter import pyname"

        try:

            logger = logging.getLogger(__name__)

            data = instance.graphManager.man.serialize()

            base_filename = f"{instance._currentFileName}"
            # base_filename = base_filename[:-8]
            python_filename = base_filename + ".py"

            pf = pathlib.Path(python_filename)

            name = pf.name[: pf.name.rfind(".")]
            base = CompositeDefinition(name, data)

            this_folder = pathlib.Path(inspect.getfile(RobinsonExporter)).parent
            template_folder = this_folder / "templates"

            mylookup = TemplateLookup(
                directories=[template_folder], imports=[f"{pyname_filter}"]
            )
            tmp = mylookup.get_template("main.py.tpl")

            buf = StringIO()
            buf.write(tmp.render(base=base))

            with open(python_filename, "w") as fh:
                fh.write(buf.getvalue())

            try:
                # os.system(f"python -m black {python_filename}")
                black.format_file_in_place(
                    pathlib.Path(python_filename),
                    mode=black.FileMode(line_length=80),
                    fast=False,
                    write_back=black.WriteBack.YES,
                )
                # black.format_file_in_place(python_filename, fast=False, mode=)
            except Exception as e:
                logger.warn("Could not format code with black")
                logger.warn(e)

            node_configs = {}

            for uuid, node in base.nodes().items():
                try:
                    cfg = node.config()

                    if cfg is None:
                        continue

                    # if isinstance(node, RobinsonQtComponent):
                    # cfg["qt_component"] = True

                    if len(cfg) > 0:
                        node_configs[node.name()] = cfg
                except Exception as e:
                    print("Error whil reading config from graph")
                    print(e)

            tmpl_config = mylookup.get_template("config.yaml.tpl")

            cfg_buffer = StringIO()

            settings = robinson.config.current()

            pprint(settings.as_dict())
            project_config = dict()

            project_config["components"] = node_configs

            yaml_str = yaml.safe_dump(dict(default=project_config), sort_keys=False)

            cfg_buffer.write(tmpl_config.render(component_config=yaml_str))

            cfg_filename = f"{base_filename}.yaml"

            with open(cfg_filename, "w") as fh:
                fh.write(cfg_buffer.getvalue())

        except Exception as e:
            print("Error while exporting graph")
            pprint(traceback.format_exception(e))
