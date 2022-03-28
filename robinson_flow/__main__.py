#!/usr/bin/env python3
import os

from PyFlow.Core.Common import SingletonDecorator
from PyFlow.Core.GraphManager import GraphManager
# os.environ['QT_API'] = 'pyside2'  # tells QtPy to use PySide2
os.environ['QT_API'] = 'pyside6'  # tells QtPy to use PySide2
# os.environ['QT_API'] = 'pyqt5'  # tells QtPy to use PySide2

import sys
from PyFlow.App import PyFlow
from Qt.QtWidgets import QApplication

import pathlib

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
    app = QApplication(sys.argv)

    instance = PyFlow.instance(software="standalone", graphManager=RobinsonGraphManagerSingleton())
    # instance.loadFromFile(str(pathlib.Path("/home/matthias/src/robinson/robinson_flow/files/mission_tracker.pygraph")))
    instance.loadFromFile(str(pathlib.Path("/home/matthias/src/robinson/robinson_flow/files/latest.pygraph")))

    if instance is not None:
        app.setActiveWindow(instance)
        instance.show()

        try:
            sys.exit(app.exec_())
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
