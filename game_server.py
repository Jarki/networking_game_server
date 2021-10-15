import socket
import threading
import logging

import player


class GameServer:
    def __init__(self, host: str, port: int) -> None:
        self.port = self.__create_server(host, port)

        self.players = []
        self.player_data = []

        self.log = []

        self.max_players = 2

    # server functions
    def __create_server(self, host: str = '', port: int = 0) -> int:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()

        return self.server.getsockname()[1]

    def get_server_port(self) -> int:
        return self.port

    def connect_players(self, players: tuple) -> None:  # a tuple of Player objects
        if len(players) > self.max_players:
            logging.warning(f"Tried to connect more players than allowed (allowed: {self.max_players}, tried to "
                            f"connect: {len(players)}")
            return

        for i in range(1, len(players)):
            player, addr = self.server.accept()  # accept a connection from a client
            self.players.append(player)  # add the connection to a list
            self.player_data.append(players[i])

            threading.Thread(target=self.receive_updates_from_player, args=(player, players[i].get_name())).start()

    def add_to_log(self, update):
        self.log.append(update)

        self.send_updates_to_players()

    def receive_updates_from_player(self, player_conn: socket.socket, player_name) -> None:
        player_conn.sendall(b'ye have connected')

        while True:
            data = player_conn.recv(1024)

            if not data:
                break

            self.add_to_log(f"player {player_name} says: {data}")

        player_conn.close()

    def send_updates_to_players(self):
        for player in self.players:
            player.sendall(self.log[-1])
