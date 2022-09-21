#!/usr/bin/env python3
import os

import robinson_flow
import robinson.config

os.environ["QT_API"] = "PyQt5"  # tells QtPy to use PySide2
os.environ["MPLBACKEND"] = "Qt5Agg"

import inspect
import sys

from PyFlow.App import PyFlow
from PyFlow.Core.Common import SingletonDecorator
from PyFlow.Core.GraphManager import GraphManager
from Qt.QtWidgets import QApplication

# os.environ['QT_API'] = 'pyside2'  # tells QtPy to use PySide2
# os.environ['QT_API'] = 'pyside6'  # tells QtPy to use PySide2
# os.environ['QT_API'] = 'pyqt5'  # tells QtPy to use PySide2

import sys
from PyFlow.App import PyFlow
from Qt.QtWidgets import QApplication
import robinson.config
import inspect

print(inspect.getmro(QApplication))
print()
import functools
import pathlib
import faulthandler

faulthandler.enable()

import robinson.logging


class RobinsonGraphManager(GraphManager):
    def Tick(self, deltaTime):
        return super().Tick(deltaTime)


@SingletonDecorator
class RobinsonGraphManagerSingleton(object):
    def __init__(self):
        self.man = RobinsonGraphManager()

    def get(self):
        """Returns graph manager instance

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


def main():

    robinson_flow.config.add_config(pathlib.Path(".") / "config/settings.yaml")
    robinson_flow.config.add_config(
        pathlib.Path(".") / "config/settings.environment.yaml"
    )

    app = QApplication(sys.argv)

    instance = PyFlow.instance(
        software="standalone", graphManager=RobinsonGraphManagerSingleton()
    )
    # instance.loadFromFile(str(pathlib.Path("/home/matthias/src/robinson/robinson_flow/files/mission_tracker.pygraph")))

    instance.loadFromFile = prefix_hook(
        instance.loadFromFile, loadFromFileHook_function
    )

    try:
        # instance.loadFromFile(str(pathlib.Path("/home/matthias/src/robinson/robinson_flow/files/latest.pygraph")))
        instance.loadFromFile(str(pathlib.Path("latest.pygraph")))
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
