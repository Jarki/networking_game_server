import socket
import threading
import logging

class SocketHandler:
    def __init__(self):
        self.server = None
        self.players = []
        self.max_players = 2

    def create_server(self):
        host = ''  # accept connections from any address
        port = 65432  # need to create a system to find a free port

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()

    def connect_players(self, amount_of_players):
        if amount_of_players > self.max_players:
            logging.warning(f"Tried to connect more players than allowed (allowed: {self.max_players}, tried to "
                            f"connect: {amount_of_players}")
            return

        for n in range(1, amount_of_players):
            player, addr = self.server.acccept()  # accept a connection from a client
            self.players.append(player)  # add the connection to a list

            threading.Thread(target=self.handle_player, args=(player, addr)).start()

    def handle_player(self, player_conn, player_addr):
        pass
