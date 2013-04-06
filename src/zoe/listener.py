import socket
import threading
from zoe.zp import *

RESET = '\033[0m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'

class Listener:
    def __init__(self, host, port, delegate, serverhost, serverport):
        self._host, self._port = host, port
        self._srvhost, self._srvport = serverhost, serverport
        self._delegate = delegate
        self._running = False

    def start(self):
        self._running = True
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self._host, self._port))
        self._socket.listen(10)
        while self._running:
            try:
                conn, addr = self._socket.accept()
                thread = threading.Thread(target = self.connection, args = (conn, addr))
                thread.start()
            except Exception as e:
                # raised when closing the server socket -> ignore it
                pass

    def connection(self, conn, addr):
        message = ""
        host, port = addr
        while True:
            data = conn.recv(1024)
            if not data: break
            message = message + data.decode("utf-8")
        conn.close()
        print (YELLOW + "RECV " + host + ":" + str(port) + " " + message + RESET)
        parser = MessageParser(message)
        tags = parser.tags()
        if "exit!" in tags:
            self.stop()
            return
        self._delegate.receive(parser)

    def stop(self):
        self._running = False
        self._socket.close()

    def send(self, message, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((host, port))
            s.sendall(message.encode("utf-8"))
            print (GREEN + "SENT " + host + ":" + str(port) + " " + message + RESET)
        except Exception as e:
            print (RED + "ERR  " + host + ":" + str(port) + " " + message + RESET)
            raise e
        finally:
            s.close()

    def sendbus(self, message):
        self.send(message, self._srvhost, self._srvport)

