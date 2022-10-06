#!/usr/bin/env python3
import os

import robinson_flow

os.environ["QT_API"] = "PyQt5"  # tells QtPy to use PySide2
os.environ["MPLBACKEND"] = "Qt5Agg"

from PyFlow.Core.Common import SingletonDecorator
from PyFlow.Core.GraphManager import GraphManager

# os.environ['QT_API'] = 'pyside2'  # tells QtPy to use PySide2
# os.environ['QT_API'] = 'pyside6'  # tells QtPy to use PySide2
# os.environ['QT_API'] = 'pyqt5'  # tells QtPy to use PySide2

import sys
from PyFlow.App import PyFlow
from Qt.QtWidgets import QApplication
import robinson_flow.config
import inspect

print(inspect.getmro(QApplication))
print()

import pathlib
import faulthandler

faulthandler.enable()


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
