import socket
import struct
import time

HOST = "localhost"  # The server's hostname or IP address
PORT = 12345  # The port used by the server

def receive(s):
    state = "l"
    expectedByteCount = 2
    bytes_received = bytearray()
    while True:
        data = s.recv(expectedByteCount)

        if data is None:
            break
        if len(data) == 0:
            break

        bytes_received += data
        expectedByteCount -= len(data)

        if expectedByteCount == 0:
            if state == "l":
                l = struct.unpack(">H", bytes_received)[0]
                state = "c"
                expectedByteCount = l
                bytes_received.clear()
            elif state == "c":
                d = bytes(bytes_received.copy())
                state = "l"
                expectedByteCount = 2
                bytes_received.clear()
                return d

should_continue = True

class Client():
    def __init__(self, socket):
        self.socket = socket
        self.state = "stop"

    def avance(self):
        if self.state != "avance":
            self._send("avance")
            self.state = "avance"
    def recule(self):
        if self.state != "recule":
            self._send("recule")
            self.state = "recule"
    def tourne_droite(self):
        if self.state != "tourne_droite":
            self._send("tourne_droite")
            self.state = "tourne_droite"
    def tourne_gauche(self):
        if self.state != "tourne_gauche":
            self._send("tourne_gauche")
            self.state = "tourne_gauche"
    def stop(self):
        if self.state != "stop":
            self._send("stop")
            self.state = "stop"

    def distance(self) -> float:
        self._send("distance")
        return float(receive(self.socket))

    def suivi_ligne(self) -> list:
        self._send("suivi_ligne")
        received = receive(self.socket).decode("utf-8")
        return list(map(int, str(received).split(";")))

    def _send(self, msg):
        b = bytearray()
        b += struct.pack(">H", len(msg))
        b += bytes(msg, encoding='utf-8')
        self.socket.sendall(b)

def wallsDetection(client):
    client.avance()
    while should_continue:
        if client.distance() < 10:
            client.stop()
            print("stopping")
            time.sleep(1)
            client.tourne_droite()
            print("turn right")
            time.sleep(.4)
            client.stop()
            print("stopping")
            time.sleep(1)
        else:
            client.avance()
            print("move forward")

def followLine(client):
    client.avance()
    lostLine = False
    onLine = False
    while should_continue:
        [colorCenter, colorRight, colorLeft] = client.suivi_ligne()
        colorCenter = (colorCenter < 3000)
        colorRight = (colorRight < 3000)
        colorLeft = (colorLeft < 3000)
        match (colorLeft, colorCenter, colorRight):
            case (False, False, False):
                client.avance()
                onLine = False
            case (False, False, True):
                lostLine = False
                client.tourne_droite()
            case (False, True, False):
                lostLine = False
                client.avance()
            case (False, True, True):
                lostLine = False
                client.tourne_droite()
            case (True, False, False):
                lostLine = False
                client.tourne_gauche()
            case (True, False, True):
                lostLine = False
                client.tourne_droite()
            case (True, True, False):
                lostLine = False
                client.tourne_gauche()
            case (True, True, True):
                lostLine = False
                client.avance()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    client = Client(s)

    mode = input("which mode?\n")
    match mode:
        case "walls":
            wallsDetection(client)
        case "line":
            followLine(client)
