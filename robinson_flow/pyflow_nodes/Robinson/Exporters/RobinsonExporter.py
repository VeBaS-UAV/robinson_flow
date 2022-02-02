import traceback
from datetime import datetime
from PyFlow.UI.UIInterfaces import IDataExporter
from PyFlow.Core.version import Version

from robinson_flow.pyflow_nodes.Robinson.Exporters.python_exporter import CompositeDefinition
from io import StringIO
from mako.lookup import TemplateLookup
import pathlib
import inspect
import toml


def pyname(name):
    return name.replace("-","_")

class RobinsonExporter(IDataExporter):
    """docstring for DemoExporter."""

    def __init__(self):
        super(RobinsonExporter, self).__init__()

    @staticmethod
    def createImporterMenu():
        return True

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

            name = pf.name[:pf.name.rfind('.')]
            base = CompositeDefinition(name, data)

            this_folder = pathlib.Path(inspect.getfile(RobinsonExporter)).parent
            template_folder = this_folder / "templates"

            mylookup = TemplateLookup(directories=[template_folder], imports=[f"{pyname_filter}"])
            tmp = mylookup.get_template("main.py.tpl")

            buf = StringIO()
            buf.write(tmp.render(base=base))

            with open(python_filename,"w") as fh:
                fh.write(buf.getvalue())


            #TODO read robinson data
            # with open(cfg_filename,"w") as fh:
                # fh.write(buf.getvalue())

            node_configs = {}

            for uuid, node in base.nodes().items():
                cfg = node.config()

                if len(cfg) > 0:
                    node_configs[node.name()] = cfg

            tmp = mylookup.get_template("config.toml.tpl")
            buf = StringIO()

            project_config= {}
            project_config["components"] = node_configs

            toml_str = toml.dumps(project_config)

            buf.write(tmp.render(component_config=toml_str))

            cfg_filename = f"{instance._currentFileName}.toml"
            with open(cfg_filename,"w") as fh:
                fh.write(buf.getvalue())

        except Exception as e:
            print("Error while exporting graph")
            print(traceback.format_exception(e))
