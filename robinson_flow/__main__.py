import faulthandler
import inspect
import os
import pathlib
import sys


import robinson_flow
import robinson.config

from PyFlow.App import PyFlow
from PyFlow.Core.Common import SingletonDecorator
from PyFlow.Core.GraphManager import GraphManager
from Qt.QtWidgets import QApplication


print(inspect.getmro(QApplication))


faulthandler.enable()


class RobinsonGraphManager(GraphManager):
    def Tick(self, deltaTime):
        return super().Tick(deltaTime)


@SingletonDecorator
class RobinsonGraphManagerSingleton(object):
    def __init__(self):
        self.man = RobinsonGraphManager()

    def get(self):
        """Return graph manager instance.

        :rtype: :class:`~PyFlow.Core.GraphManager.GraphManager`
        """
        return self.man


def prefix_hook(function, prefunction):
    def run(*args, **kwargs):
        prefunction(*args, **kwargs)
        return function(*args, **kwargs)

    return run


def loadFromFileHook_function(*args, **kwargs):
    cfg_file = pathlib.Path(args[0] + ".yaml")
    print("Loading file...", cfg_file)
    robinson.config.merge_config(cfg_file)
    robinson.logging._executable_name = cfg_file.stem

    with open(".latest.pyflow", "w") as fh:
        fh.write(args[0])


def main():

    robinson.config.add_config(pathlib.Path(".") / "config/settings.yaml")
    robinson.config.add_config(pathlib.Path(".") / "config/settings.environment.yaml")
    robinson.config.add_config(pathlib.Path(os.environ["ROBINSON_WS"]) / "config.yaml")

    app = QApplication(sys.argv)

    robinson.config.current()

    instance = PyFlow.instance(
        software="standalone", graphManager=RobinsonGraphManagerSingleton()
    )

    instance.loadFromFile = prefix_hook(
        instance.loadFromFile, loadFromFileHook_function
    )

    try:
        with open(".latest.pyflow", "r") as fh:
            file = fh.read().replace("\n", "")
            instance.loadFromFile(str(pathlib.Path(file)))

    except Exception as e:
        print(e)
    if instance is not None:
        app.setActiveWindow(instance)
        instance.show()

        try:
            sys.exit(app.exec_())
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
