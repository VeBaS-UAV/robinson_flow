import traceback
from datetime import datetime
from typing import OrderedDict
from PyFlow.UI.UIInterfaces import IDataExporter
from PyFlow.Core.version import Version

from robinson.components.qt import RobinsonQtComponent

from io import StringIO
from mako.lookup import TemplateLookup
import pathlib
import inspect

# import toml as serializer
# import yaml as serializer
import yaml
from pprint import pprint
import robinson_flow.config

from robinson_flow.pyflow_nodes.Robinson.Exporters.parser_classes import (
    CompositeDefinition,
)


def pyname(name):
    return name.replace("-", "_").replace("/", "_")


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
            data = instance.graphManager.man.serialize()

            python_filename = f"{instance._currentFileName}.py"
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
            tmpl_env_config = mylookup.get_template("config.env.yaml.tpl")
            tmpl_local_config = mylookup.get_template("config.local.yaml.tpl")

            cfg_buffer = StringIO()
            cfg_env_buffer = StringIO()
            cfg_local_buffer = StringIO()

            settings = robinson_flow.config.current()
            project_config = dict()
            project_env_config = dict()
            project_local_config = dict()

            # project_config["environment"]= settings.as_dict()["ENVIRONMENT"]
            project_config["environment"] = dict()
            project_env_config["environment"] = dict(dynaconf_merge=True, connectors={})
            project_local_config["dynaconfig_merge"] = True

            envsettings = settings.environment
            envsettings_env = settings.environment.connectors

            for group_key in envsettings.keys():
                group_config = envsettings[group_key]
                group = dict()

                try:
                    for part_key in group_config.keys():
                        group[part_key] = {**group_config[part_key]}

                    project_config["environment"][group_key] = group
                except Exception as e:
                    print(
                        f"Could not export group {group_key} with value {group_config}"
                    )

            project_env_config["environment"]["connectors"] = project_config[
                "environment"
            ]["connectors"]
            del project_config["environment"]["connectors"]

            project_config["components"] = node_configs

            yaml_str = yaml.safe_dump(dict(default=project_config), sort_keys=False)
            yaml_env_str = yaml.safe_dump(
                dict(default=project_env_config), sort_keys=False
            )
            yaml_local_str = yaml.safe_dump(
                dict(default=project_local_config), sort_keys=False
            )

            cfg_buffer.write(tmpl_config.render(component_config=yaml_str))
            cfg_env_buffer.write(tmpl_env_config.render(component_config=yaml_env_str))
            cfg_local_buffer.write(
                tmpl_local_config.render(component_config=yaml_local_str)
            )

            cfg_filename = f"{instance._currentFileName}.yaml"
            with open(cfg_filename, "w") as fh:
                fh.write(cfg_buffer.getvalue())
            cfg_env_filename = f"{instance._currentFileName}.env.yaml"
            with open(cfg_env_filename, "w") as fh:
                fh.write(cfg_env_buffer.getvalue())

            # do not overwrite
            # cfg_local_filename = f"{instance._currentFileName}.local.yaml"
            # with open(cfg_local_filename,"w") as fh:
            #     fh.write(cfg_local_buffer.getvalue())

        except Exception as e:
            print("Error while exporting graph")
            pprint(traceback.format_exception(e))
