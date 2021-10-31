import socket
import threading
import logging

from player import Player


class GameServer:
    def __init__(self, host: str = '', port: int = 0) -> None:
        self.port = self.__create_server(host, port)
        logging.debug(f"Raised on port {self.port}")

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

    # def connect_players(self, players: tuple) -> None:  # a tuple of Player objects
    #     logging.debug(f"Waiting for {len(players)} players")
    #
    #     if len(players) > self.max_players:
    #         logging.warning(f"Tried to connect more players than allowed (allowed: {self.max_players}, tried to "
    #                         f"connect: {len(players)}")
    #         return
    #
    #     for i in range(0, len(players)):
    #         player, addr = self.server.accept()  # accept a connection from a client
    #
    #         logging.debug(f"Received a connection from address: {addr}, player: {players[i].get_name()}")
    #
    #         self.players.append(player)  # add the connection to a list
    #         self.player_data.append(players[i])
    #
    #         threading.Thread(target=self.receive_updates_from_player, args=(player, players[i].get_name())).start()

    def wait_for_players(self):
        logging.debug(f'Waiting for {self.max_players} players')

        while self.max_players - len(self.players):
            player_conn, addr = self.server.accept()

            if player_conn.recv(1024) != b'want connect':
                continue

            player_conn.sendall(b'connected')
            player_data = player_conn.recv(1024)

            self.players.append(player_conn)
            self.add_to_log(str.encode(f'Player {player_data} has connected'))

            self.player_data.append(player_data)
            threading.Thread(target=self.receive_updates_from_player, args=(player_conn, player_data)).start()

    def add_to_log(self, update):
        self.log.append(update)

        self.send_updates_to_players()

    def receive_updates_from_player(self, player_conn: socket.socket, player_name) -> None:
        while True:
            data = player_conn.recv(1024)

            if not data:
                break

            action = f"Player {player_name} says: {data}"

            self.add_to_log(str.encode(action))

        player_conn.close()

    def send_updates_to_players(self):
        for player in self.players:
            player.sendall(self.log[-1])
