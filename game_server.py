import socket
import threading
import logging

from player import Player


class GameServer:
    def __init__(self, host: str = '', port: int = 0) -> None:
        self.port = self.__create_server(host, port)
        logging.debug(f"Raised on port {self.port}")

        self.players = []

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

    def handle_connection(self, player_connection, addr):
        logging.debug(f'Accepted a connection from {addr}')

        if player_connection.recv(1024) != b'want connect':
            return

        player_connection.sendall(b'connected')
        player_data = player_connection.recv(1024)

        player = Player(player_data)
        player.store_connection(player_connection)

        existing_player = self.__get_player_in_game(player)
        if existing_player is not None:
            logging.debug(f'Player {player.name} is already in game')
            if not self.__is_player_connected(player):
                logging.debug(f'Player {player.name} is not connected')
                existing_player.store_connection(player_connection)
                self.handle_reconnect(existing_player)

            return

        if self.__is_full():
            return

        self.players.append(player)

        msg = f'Player {player.name} has connected'

        logging.debug(msg)
        self.add_to_log(msg)

        threading.Thread(target=self.receive_updates_from_player, args=[player]).start()

    def wait_for_players(self):
        logging.debug(f'Waiting for {self.max_players} players')

        while True:
            player_conn, addr = self.server.accept()

            self.handle_connection(player_conn, addr)

    def add_to_log(self, update: str):
        self.log.append(str.encode(update))

        self.send_updates_to_players()

    def receive_updates_from_player(self, player: Player) -> None:
        while True:
            try:
                data = player.connection.recv(1024)
                if not data:
                    break

                action = f"Player {player.name} says: {data}"

                logging.debug(action)
                self.add_to_log(action)
            except ConnectionResetError:
                player.store_connection(None)

                msg = f'Player {player.name} has disconnected. They have 60 seconds to reconnect.'

                logging.debug(msg)
                self.add_to_log(msg)

                return

        player.connection.close()

    # functions to access certain players
    def __get_player_in_game(self, target_player: Player) -> Player:
        for player in self.players:
            if player.name == target_player.name:
                return player

        return

    def __is_player_connected(self, target_player: Player):
        for player in self.players:
            if player.name == target_player.name:
                return player.is_connected()

        return

    def __is_full(self):
        return not (self.max_players - len(self.players)) # if full, max - len(players) will be 0, not 0 = True

    def handle_reconnect(self, player: Player):
        msg = f'Player {player.name} has reconnected'

        logging.debug(msg)
        self.add_to_log(msg)

        threading.Thread(target=self.receive_updates_from_player, args=[player]).start()

    def send_updates_to_players(self):
        for player in self.players:
            if player.is_connected():
                print(f'sending a message to player {player.name}')
                player.connection.sendall(self.log[-1])
