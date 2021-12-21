import socket
import threading
import logging
import random
import re
import time
from typing import Optional

from player import Player
from update import Update, UpdateTypes
from game import Game
from dbmanager import DBManager


class GameServer:
    def __init__(self, host: str = '', port: int = 0) -> None:
        self.port = self.__create_server(host, port)
        logging.debug(f"Raised on port {self.port}")

        self.players: list[Player] = []

        self.log: list[Update] = []

        self.max_players = 2
        self.players_connected = 0
        self.players_want_to_end = 0
        self.first_move = ""

        self.game = None

        self.board_size = -1
    # server functions

    def __create_server(self, host: str = '', port: int = 0) -> int:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        return self.server.getsockname()[1]

    def wait_for_players(self):
        logging.debug(f'Waiting for {self.max_players} players')

        while True:
            player_conn, addr = self.server.accept()
            if self.__is_full():
                player_conn.close()
                continue

            self.connect_new_player(player_conn, addr)

    def connect_new_player(self, player_connection, addr) -> None:
        logging.debug(f'Accepted a connection from {addr}')

        if player_connection.recv(1024) != b'want connect':
            player_connection.close()
            return

        player_connection.sendall(b'connected')
        player_data = player_connection.recv(1024)

        player = Player(player_data.decode('utf-8'))
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
            player_connection.close()
            return

        self.players.append(player)
        self.players_connected += 1

        self.send_player_stats(player)

        if self.__is_full():
            logging.debug('Player 2/2 has connected')
            self.start_game()
            return

        logging.debug('Player 1/2 has connected')
        player.send_message('choose')

        size: str = player.connection.recv(1024).decode('utf-8')
        size = size.replace('size:', '')

        self.board_size = int(size)
        print('set board size')
        print(self.board_size)

    def send_player_stats(self, player: Player) -> None:
        player_stats = DBManager.get_player_stats(player.name)
        player.send_message(f'stats:{player_stats[0]}:{player_stats[1]}:{player_stats[2]}')

    def start_game(self) -> None:
        while self.board_size < 0:
            time.sleep(1)

        logging.debug('Starting the game')

        for i in range(self.players_connected):
            for j in range(self.players_connected):
                if i == j:
                    continue

                self.players[i].send_message(f'size:{self.board_size}')
                self.players[i].send_message(f'opponent:{self.players[j].name}')

        self.game = Game(self.players[0].name, self.players[1].name, self.board_size * 2)

        starting = self.players[random.randint(0, 1)].name  # deciding who makes the first turn
        self.game.set_active_player(starting)
        self.first_move = starting

        self.game.set_gameover_handler(self.handle_game_result)

        self.game.reset_timer()

        time.sleep(1)

        for player in self.players:
            player.send_message(f'start:{starting}')
            threading.Thread(target=self.receive_updates_from_player, args=[player]).start()

    def handle_game_result(self, result: str) -> None:
        if result == ":draw:":
            DBManager.record_draw(
                self.players[0].name,
                self.players[1].name
            )
            self.end_game(result)
            return

        winner = result
        loser = self.__get_opponent(winner).name

        DBManager.record_win(winner, loser)
        self.end_game(winner)

    def end_game(self, winner: str) -> None:
        for player in self.players:
            player.send_message(f'winner:{winner}')
            player.disconnect()

        self.server.shutdown(socket.SHUT_RDWR)
        self.server.close()

    def receive_updates_from_player(self, player: Player) -> None:
        while True:
            try:
                data = player.connection.recv(1024)

                action: bytes = data

                logging.debug(action)

                if action.decode('utf-8').startswith('msg:'):
                    self.add_to_log(Update(action, player, UpdateTypes.MESSAGE_UPDATE))
                    continue

                if action.decode('utf-8') == 'leave' or action.decode('utf-8') == 'unleave':
                    if action.decode('utf-8') == 'leave':
                        self.players_want_to_end += 1
                    else:
                        self.players_want_to_end -= 1

                    self.add_to_log(Update(action.decode('utf-8'), player))

                    if self.max_players == self.players_want_to_end:
                        winner = self.game.determine_winner()

                        self.handle_game_result(winner)
                    continue

                pattern = re.compile('push\\([0-9]+, ?[0-9]+\\)')
                string = action.decode('utf-8')

                if pattern.match(string) is not None:
                    # message looks like push(0,0)
                    string = string.replace('push', '')  # remove the word push
                    string = string[1:-1].split(',')  # remove round brackets and split
                    string = map(lambda x: int(x), string)  # convert everything to int

                    self.game.push_tile(tuple(string))  # make a tuple and update

                    self.add_to_log(Update(action, player))
            except (ConnectionResetError, ConnectionAbortedError):
                player.store_connection(None)
                self.players_connected -= 1

                msg = f'disconnect:{player.name}'

                logging.debug(msg)
                self.add_to_log(Update(msg, player))

                return

        player.connection.close()

    def handle_reconnect(self, player: Player) -> None:
        msg = f'reconnect:{player.name}'

        logging.debug(msg)
        self.add_to_log(Update(msg, player))

        self.send_player_stats(player)
        player.send_message(f'start:{self.first_move}')
        player.send_message(f'opponent:{self.__get_opponent(player.name).name}')

        threading.Thread(target=self.receive_updates_from_player, args=[player]).start()

        for entry in self.log:
            player.send_message(entry.msg)

        player.send_message(f'start:{self.game.get_active_player()}')

    def add_to_log(self, update: Update):
        self.log.append(update)

        self.send_updates_to_players()

    def get_server_port(self) -> int:
        return self.port

    def __get_player_in_game(self, target_player: Player) -> Optional[Player]:
        for player in self.players:
            if player.name == target_player.name:
                return player

        return None

    def __get_opponent(self, target_player: str) -> Optional[Player]:
        for player in self.players:
            if player.name != target_player:
                return player

        return None

    def __is_player_connected(self, target_player: Player) -> bool:
        for player in self.players:
            if player.name == target_player.name:
                return player.is_connected()

        return False

    def __is_full(self):
        return self.max_players - self.players_connected <= 0

    def send_updates_to_players(self):
        for player in self.players:
            if self.log[-1].type == UpdateTypes.MESSAGE_UPDATE:
                if player.is_connected():
                    player.send_message(self.log[-1].msg)
            else:
                if self.log[-1].player != player:
                    if player.is_connected():
                        player.send_message(self.log[-1].msg)
