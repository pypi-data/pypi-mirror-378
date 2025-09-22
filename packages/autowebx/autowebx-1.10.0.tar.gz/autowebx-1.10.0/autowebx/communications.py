"""Very small localhost message-passing helpers.

Note: `send(msg)` opens a Listener and writes to the first client. Use
`receive()` to connect as a Client and read the message. Run the sender
first so the listener is available.
"""

from multiprocessing.connection import Listener
from multiprocessing.connection import Client
from threading import Lock

__lock = Lock()


def send(msg):
    with Listener(('localhost', 3011)) as listener:
        with listener.accept() as conn:
            conn.send(msg)


def receive():
    with __lock:
        try:
            with Client(('localhost', 3011)) as conn:
                return conn.recv()
        except ConnectionRefusedError:
            raise ConnectionRefusedError("Run the sender first")
