import sys

# python -m pip install PySide2  #

from PySide2.QtWidgets import (QLineEdit, QPushButton, QApplication,
                               QVBoxLayout, QDialog)
from PySide2.QtCore import *

# python -m pip install "python-socketio[client]"  #

import socketio

url = 'ws://localhost:5000'
transport = 'websocket'
myroom = "pythonclient"

sio = socketio.Client()


class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.startbutton = QPushButton("start")
        self.stopbutton = QPushButton("stop")
        self.setFixedSize(300, 300)
        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.startbutton)
        layout.addWidget(self.stopbutton)
        # Set dialog layout
        self.setLayout(layout)
        # Add button signal to greetings slot
        self.startbutton.clicked.connect(self.start)
        self.stopbutton.clicked.connect(self.stop)

    def start(self):
        self.startclient(url, myroom, transport)

    def stop(self):
        self.stopclient()

    def startclient(self, url, myroom, transport):
        my_thread = DummyWorker()

        if sio.sid:
            my_thread.logger_emiter.emit("Already connected")

        else:
            sio.connect(url, transports=transport)

            @sio.on('connect')
            def connect():
                my_thread.logger_emiter.emit("'Connected id  " + sio.sid)
                sio.emit('room', myroom)
                my_thread.logger_emiter.emit('Joined room  '+ myroom)

            @sio.on('message')
            def message(data):
                my_thread.logger_emiter.emit('Received message!' + data)

            @sio.on('join')
            def join(room):
                my_thread.logger_emiter.emit('Joined room  ' + room)

            @sio.on('connect_error')
            def connect_error():
                my_thread.logger_emiter.emit("Connection failed!")

            @sio.on('disconnect')
            def disconnect():
                my_thread.logger_emiter.emit("Disconnected!")
                sio.disconnect()

    def stopclient(self):
        print('Stop Client')
        sio.disconnect()


class DummyWorker(QThread):
    # Signals must be class vars
    logger_emiter = Signal(str)

    def __init__(self):
        super().__init__()

        # send to the main thread explicitly
        self.logger_emiter.connect(self.main_log, Qt.QueuedConnection)
        print("DummyWorker created")

    @Slot(str)
    def main_log(self, s):
        # logging must be on the main thread,
        # else iClone crashes because it logs to UI thread
        print(s)


app = QApplication(sys.argv)

window = Form()
window.show()

app.exec_()