import threading
import logging
from typing import Optional


class Game:
    def __init__(self, player1_name, player2_name):
        self.p1 = player1_name
        self.p2 = player2_name

        self.player_points = {
            self.p1: 0,
            self.p2: 0
        }

        self.size = 22
        self.board: list[list[int]] = [[0] * self.size for i in range(self.size)]
        self.generate_board()

        self.player1_active = True

        self.on_game_over = lambda x: x  # this function is supposed to take 1 argument - player name

        self.timer: Optional[threading.Timer] = None
        self.timeout_time = 5

    def set_active_player(self, player: str) -> None:
        if player == self.p1:
            self.player1_active = True
        else:
            self.player1_active = False

    def get_active_player(self):
        if self.player1_active:
            return self.p1
        else:
            return self.p2

    def reset_timer(self):
        if self.timer is not None:
            self.timer.cancel()

        timeout_winner = self.p1
        if self.player1_active:
            timeout_winner = self.p2

        logging.debug(f'Timing out, player is about to win {timeout_winner}')
        self.timer = threading.Timer(self.timeout_time, self.on_game_over, args=[timeout_winner])
        self.timer.start()

    def toggle_active_player(self) -> None:
        self.player1_active = not self.player1_active

    def give_point(self) -> None:
        if self.player1_active:
            self.player_points[self.p1] += 1
        else:
            self.player_points[self.p2] += 1

        if self.is_game_over():
            self.on_game_over(self.determine_winner())

    def determine_winner(self) -> str:
        if self.player_points[self.p1] > self.player_points[self.p2]:
            return self.p1
        elif self.player_points[self.p1] < self.player_points[self.p2]:
            return self.p2
        else:
            return ":draw:"

    def set_gameover_handler(self, callback) -> None:
        self.on_game_over = callback

    def is_game_over(self) -> bool:
        if self.player_points[self.p1] + self.player_points[self.p2] >= 60:
            return True

        return False

    def push_tile(self, pos: tuple[int, int]) -> None:
        i, j = pos[0], pos[1]

        is_vertical = not self.board[i][j]
        self.board[i][j] = 2

        need_toggle = True

        if is_vertical:
            if self.check_if_closed(i, j - 1) == 8:
                need_toggle = False
                self.give_point()

            if self.check_if_closed(i, j + 1) == 8:
                need_toggle = False
                self.give_point()
        else:
            if self.check_if_closed(i + 1, j) == 8:
                need_toggle = False
                self.give_point()

            if self.check_if_closed(i - 1, j) == 8:
                need_toggle = False
                self.give_point()

        if need_toggle:
            self.toggle_active_player()

        self.reset_timer()

    def check_if_closed(self, i: int, j: int) -> int:
        if self.__is_in_bounds((i, j)):
            tiles = [self.board[i][j - 1], self.board[i - 1][j], self.board[i][j + 1], self.board[i + 1][j]]

            conclusion = 0

            tile: int
            for tile in tiles:
                conclusion += tile

            return conclusion

        return -1

    def generate_board(self, size=10) -> None:
        cutout_num = 0

        self.size = size * 2 + 2

        for i in range(self.size):
            if i < 11:
                if not i % 2:
                    cutout_num = i + 2

            if i >= 11:
                if i % 2:
                    cutout_num = i - 2 * abs(20 / 2 - i) + 1
            for j in range(self.size):
                value = -1

                if not i % 2:
                    if j % 2:
                        value = 1  # horizontal
                else:
                    if not j % 2:
                        value = 0  # vertical

                self.board[i][j] = value

    def __is_in_bounds(self, indexes: tuple) -> bool:
        if (indexes[0] > 0 and indexes[1] > 0) and (indexes[1] < self.size - 1 and indexes[0] < self.size - 1):
            return True

        return False
