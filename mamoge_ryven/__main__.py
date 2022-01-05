# %gui qt5
#!/usr/bin/env python3
# Qt
# %gui qt5
import sys
import os

from vebas.components.common import MqttTopicFilter
# os.environ['QT_API'] = 'pyside2'  # tells QtPy to use PySide2
os.environ['QT_API'] = 'pyqt5'  # tells QtPy to use PySide2
# from qtpy.QtWidgets import QMainWindow, QApplication, QMenuBar, QToolbar

from PyQt5.QtWidgets import QMainWindow, QApplication, QToolBar, QMenuBar, QAction

# ryvencore-qt
import ryvencore_qt as rc
import nodes
import threading
import time
import json
import queue

import vebas.config
vebas.config.default_logging_settings()

from ryvencore_qt.src.Design import FlowTheme_Blender as FlowTheme

# if __name__ == "__main__":

from ryvencore.FlowExecutor import FlowExecutor

from nodes import ExternalSource, export_nodes
from widgets import export_widgets

from vebas.messaging import MQTTConnection
import vebas.config
from functools import partial
config = vebas.config.default_config()

# %%
class RobinsonFlowExecutor(FlowExecutor):


    def call_external_source(self, external_source, msg):
        print("call_external_source", external_source, msg)

        external_source.set_output_val(0,msg)

    def receive_from_external_sink(self, es, topic, msg):
        print("Received from external sink", topic, msg)

        self.mqtt.publish(topic, msg)

    def __init__(self, flow):
        self.flow = flow
        self.running = False
        self.thread = None

        self.ext_sources = [n for n in self.flow.nodes if isinstance(n,nodes.ExternalSource)]
        self.ext_sink = [n for n in self.flow.nodes if isinstance(n,nodes.ExternalSink)]

        self.mqtt = MQTTConnection("mqtt", config["mqtt"]["server_uri"])
        self.mqtt.init()

        for es in self.ext_sources:
            topic = es.get_topic()
            self.mqtt.mqtt_output(topic).connect(partial(self.call_external_source, es))
            print("register topic ", topic)
        print("external sources", self.ext_sources)
        # self.start()

        for es in self.ext_sink:
            topic = es.get_topic()

            if topic is None:
                print("Topic is none for sink ", es)
                continue

            print("Register sink for topic ", topic)
            es.external_output.connect(partial(self.receive_from_external_sink, es, topic))


    # Node.update() =>
    def update_node(self, node, inp):
        print("flow update_node", node, inp)
        pass

    # Node.input() =>
    def input(self, node, index):
        print("flow input", node, index)
        pass

    # Node.set_output_val() =>
    def set_output_val(self, node, index, val):
        print("flow output", node, index, val)
        pass

    # Node.exec_output() =>
    def exec_output(self, node, index):
        print("flow exec output", node, index)
        pass


    def start(self):

        self.running = False
        if self.thread:
            self.thread.join()

        self.thread = threading.Thread(target=self.run)

        self.thread.start()

    def run(self):

        self.running = True
        while(self.running):
            self.step()
            time.sleep(0.1)

        self.cleanup()

    def cleanup(self):
        self.running = False
        self.mqtt.cleanup()


    def step(self):

        if True:
            return

        node_stack = queue.Queue()
        nodes = filter(lambda n: len(n.inputs)==0 or all([len(p.connections)==0 for p in n.inputs]),self.flow.nodes)

        call_set = set()

        for n in nodes:
            node_stack.put(n)
            call_set.add(n)


        # print("executing stack on queue", node_stack, node_stack.empty())
        while not node_stack.empty():
            n = node_stack.get(block=False)
            # print("Call update on node ", n)
            n.update_event()

            for suc in self.flow.node_successors[n]:
                if suc not in call_set:
                    node_stack.put(suc)
                    call_set.add(suc)
    def stop(self):
        self.running = False

        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None

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

# sys.exit(app.exec_())

# %%
