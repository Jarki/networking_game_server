import logging


class Player:
    def __init__(self, name=""):
        self.name = name

        self.connection = None

        self.has_reconnected = False

    def record_reconnection(self):
        self.has_reconnected = True

    def store_connection(self, conn):
        logging.debug(f'New connection stored: {conn}')
        self.connection = conn

    def send_message(self, msg):
        if type(msg) == bytes:
            msg = msg.decode('utf-8')

        msg = f'{msg}/%%'
        msg = msg.encode()

        logging.debug(f'Sending a message: {msg} to player {self.name}')
        self.connection.sendall(msg)

    def is_connected(self):
        return self.connection is not None

    def to_string(self):
        return f'{self.name}'
