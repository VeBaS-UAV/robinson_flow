from ryvencore_qt import \
        Node as Node, \
        IWB as IWB, \
        MWB as MWB

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QSlider
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics, QFont

class ExternalSinkWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)

        self.setLayout(QHBoxLayout())
        self.topic = QLineEdit()

        self.setStyleSheet('''
            QWidget{
                color: white;
                background: transparent;
                border-radius: 4px;
            }
                    ''')
        self.topic.setFont(QFont('source code pro', 10))

        self.topic.setPlaceholderText('topic')

        self.topic.editingFinished.connect(self.topic_changed)

        self.layout().addWidget(self.topic)

    def get_state(self) -> dict:
        print("getting state")
        return {
            'topic': self.topic.text()
        }

    def set_state(self, data: dict):
        self.topic.setText(data['topic'])
        self.topic_changed()
        pass

    def topic_changed(self):
        self.node.topic = self.topic.text()

class ExternalSourceWidget(MWB, QWidget):
    def __init__(self, params):
        MWB.__init__(self, params)
        QWidget.__init__(self)

        self.setLayout(QHBoxLayout())
        self.topic = QLineEdit()

        self.setStyleSheet('''
            QWidget{
                color: white;
                background: transparent;
                border-radius: 4px;
            }
                    ''')
        self.topic.setFont(QFont('source code pro', 10))

        self.topic.setPlaceholderText('topic')

        self.topic.editingFinished.connect(self.topic_changed)

        self.layout().addWidget(self.topic)

    def get_state(self) -> dict:
        print("getting state")
        return {
            'topic': self.topic.text()
        }

    def set_state(self, data: dict):
        self.topic.setText(data['topic'])
        self.topic_changed()
        pass

    def topic_changed(self):
        self.node.topic = self.topic.text()

# class ExternalSourceInputTopicWidget(IWB, QLineEdit):
#     def __init__(self, params):
#         IWB.__init__(self, params)
#         QLineEdit.__init__(self)

#         self.setStyleSheet('''
#             QLineEdit{
#                 color: white;
#                 background: transparent;
#                 border-radius: 4px;
#             }
#                     ''')
#         self.setFont(QFont('source code pro', 10))

#         self.setPlaceholderText('topic')
#         self.editingFinished.connect(self.update_node)

#         # self.resize(10,10)


#     # override this from IWB
#     def get_val(self):
#         return self.text()

#     # triggered when the input is connected and it received some data
#     def val_update_event(self, val):
#         self.setText(str(val))

#     def get_state(self) -> dict:
#         print("getting state")
#         return {
#             'topic': self.get_val()
#         }

#     def set_state(self, data: dict):
#         self.setText(data['topic'])
#         # print("setting state", data)
#         pass


def export_widgets():
    return [
        ExternalSourceWidget,
        ExternalSinkWidget
        # ExternalSinkTopicWidget
        ]
