#!/usr/bin/env python3
import os

from PyFlow.Core.Common import SingletonDecorator
from PyFlow.Core.GraphManager import GraphManager
os.environ['QT_API'] = 'pyside2'  # tells QtPy to use PySide2
# os.environ['QT_API'] = 'pyqt5'  # tells QtPy to use PySide2

import sys
from PyFlow.App import PyFlow
from Qt.QtWidgets import QApplication

import robinson.components


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
    if instance is not None:
        app.setActiveWindow(instance)
        instance.show()

        try:
            sys.exit(app.exec_())
        except Exception as e:
            print(e)


if __name__ == '__main__':
    main()
