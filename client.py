import socket
import struct

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

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while should_continue:
        msg = input("Please type message\n")
        b = bytearray()
        b += struct.pack(">H", len(msg))
        b += bytes(msg, encoding='utf-8')
        s.sendall(b)
        if msg == "distance":
            print(receive(s))
        if msg == "suivi_ligne":
            print(receive(s))