# %gui qt5
#!/usr/bin/env python3
# Qt
# %gui qt5
import sys
import os

from mamoge_ryven.mamoge import nodes
# os.environ['QT_API'] = 'pyside2'  # tells QtPy to use PySide2
os.environ['QT_API'] = 'pyqt5'  # tells QtPy to use PySide2
# from qtpy.QtWidgets import QMainWindow, QApplication, QMenuBar, QToolbar

from PyQt5.QtWidgets import QMainWindow, QApplication, QToolBar, QMenuBar, QAction

# ryvencore-qt
import ryvencore_qt as rc
import json

import vebas.config
vebas.config.default_logging_settings()

from ryvencore_qt.src.Design import FlowTheme_Blender as FlowTheme

from mamoge_ryven.mamoge import nodes as nodes
from mamoge_ryven.mamoge.nodes import export_nodes
from mamoge_ryven.mamoge.executor import RobinsonFlowExecutor

import vebas.config
config = vebas.config.default_config()

# %%

# first, we create the Qt application and a window
app = QApplication([])

class RobinsonMainWindow(QMainWindow):


    def __init__(self, session) -> None:
        super().__init__()

        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)

        self.toolBar = QToolBar("Edit", self)
        self.addToolBar(self.toolBar)

        self.saveAction = QAction(self)
        self.saveAction.setText("&Save")
        self.saveAction.triggered.connect(self.save)
        self.toolBar.addAction(self.saveAction)

        self.loadAction = QAction(self)
        self.loadAction.setText("&Load")
        self.loadAction.triggered.connect(self.load)
        self.toolBar.addAction(self.loadAction)

        self.stepAction = QAction(self)
        self.stepAction.setText("&Step")
        self.stepAction.triggered.connect(self.stepExecution)
        self.toolBar.addAction(self.stepAction)

        self.startAction = QAction(self)
        self.startAction.setText("&Start")
        self.startAction.triggered.connect(self.startExecution)
        self.toolBar.addAction(self.startAction)

        self.endAction = QAction(self)
        self.endAction.setText("&End")
        self.endAction.triggered.connect(self.stopExecution)
        self.toolBar.addAction(self.endAction)

        self.reloadAction = QAction(self)
        self.reloadAction.setText("&Reload")
        self.reloadAction.triggered.connect(self.reload)
        self.toolBar.addAction(self.reloadAction)

        self.exitAction = QAction(self)
        self.exitAction.setText("&Exit")
        self.exitAction.triggered.connect(self.exit)
        self.toolBar.addAction(self.exitAction)

# now we initialize a new ryvencore-qt session
        self.session = session

        self.init()

    def init(self):

        # self.session.design.set_flow_theme(name='pure light')  # setting the design theme
        self.session.design.set_flow_theme(theme=FlowTheme())  # setting the design theme
         # and register our nodes

        self.session.nodes.clear()
        self.session.register_nodes(export_nodes())
        # self.session.register_widgets(export_widgets())

        # to get a flow where we can place nodes, we need to crate a new script
        if len(self.session.scripts) == 0:
            self.script = self.session.create_script('hello world', flow_view_size=[1920, 1080])
            # self.script = self.session.create_script('hello world')
        else:
            self.script = self.session.scripts[-1]

        self.flow = self.script.flow
        self.script.flow.executor = RobinsonFlowExecutor(self.script.flow)
        self.executor = self.flow.executor
        self.flow.node_added.connect(self.executor.node_added)
        self.flow.node_removed.connect(self.executor.node_removed)

        # getting the flow widget of the newly created self.script
        flow_view = self.session.flow_views[self.script]
        self.setCentralWidget(flow_view)  # and show it in the main window



    def stepExecution(self):
        self.executor.step()
        pass

    def startExecution(self):
        self.executor.start()

    def stopExecution(self):
        self.executor.stop()

    def exit(self):
        self.executor.cleanup()
        sys.exit(0)

    def reload(self):

        # print(self.session.nodes)
        import importlib
        importlib.reload(nodes)
        self.session.nodes.clear()
        self.session.register_nodes(export_nodes())

        self.init()
        # pass

    def save(self):
        sd = self.session.serialize()
        json.dump(sd, open("data.json","w"))

    def load(self):

        self.executor.cleanup()

        sd = open('data.json','r')
        data = json.load(sd)

        for sc in self.session.scripts:
            self.session.delete_script(sc)

        self.session.load(data)

        self.init()

session = rc.Session()
                # finally, show the window and run the application
mw = RobinsonMainWindow(session)

mw.show()
# app.exec_()


script = session.scripts[0]

flow = script.flow

sys.exit(app.exec_())

# %%
