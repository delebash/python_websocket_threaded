
import websocket
from threading import Thread, Event

url = 'ws://localhost:5000'
transport = 'websocket'
myroom = "pythonclient"


class StartConnect(object):
    def __init__(self):
        """Constructor"""
        self.host = ''

        self.ws = None

    def connect(self):
        self.host = url
        self.ws = websocket.WebSocketApp(self.host,
                                         on_message=self.on_message,
                                         on_open=self.on_open)

        self.thread = Thread(target=self.ws.run_forever, args=(None, None, 60, 30))
        self.thread.start()

    def on_open(self, ws):
        print('open')

    def on_message(self, ws, message):
        print('msg')


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

    # def run(self):
    #     # time.sleep(2)
    #     # print(f"worker finished.") crashes - no printing from another thread in iClone!
    #     self.logger_emiter.emit("DummyWorker slept")
    @staticmethod
    def connectserver():
        my_thread = DummyWorker()
        my_thread.logger_emiter.emit("connecting")

        if sio.sid:
            my_thread.logger_emiter.emit("Already connected")
        else:
            sio.connect(url, transports=transport)

        # Note: print statment crashes iClone main thread need to do print statment on different thread
        # https://forum.reallusion.com/443699/Python-API-background-threads-crashing

        @sio.on('connect')
        def connect():
            my_thread.logger_emiter.emit("connected")
            sio.emit('room', myroom)
            # print('Joined room  ' + myroom)

        @sio.on('message')
        def message(data):
            my_thread.logger_emiter.emit('data')
            # # print('Received message!', data)
            # proccessmocapdata(data)

        @sio.on('join')
        def join(room):
            print('Joined room  ', room)
        #
        # @sio.on('connect_error')
        # def connect_error():
        #     print("Connection failed!")

        @sio.on('disconnect')
        def disconnect():
            my_thread.logger_emiter.emit("Disconnected")
            sio.disconnect()


def stopclient():
    print("Client stopped!")
    sio.disconnect()
