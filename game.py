class Game:
    def __init__(self):
        self.player1_points: int = 0
        self.player2_points: int = 0

        self.size = 22
        self.board: list[list[int]] = [[0] * self.size for i in range(self.size)]
        self.generate_board()

        self.player1_active = True

    def toggle_active_player(self):
        self.player1_active = not self.player1_active

    def give_point(self):
        if self.player1_active:
            self.player1_points += 1
        else:
            self.player2_points += 1

        print('Points:')
        print(f'Player1: {self.player1_points}')
        print(f'Player2: {self.player2_points}')

    def push_tile(self, pos: tuple[int, int]):
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

    def check_if_closed(self, i: int, j: int) -> int:
        if self.__is_in_bounds((i, j)):
            tiles = [self.board[i][j - 1], self.board[i - 1][j], self.board[i][j + 1], self.board[i + 1][j]]

            conclusion = 0

            tile: int
            for tile in tiles:
                conclusion += tile

            return conclusion

        return -1

    def generate_board(self, size=10):
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

    def __is_in_bounds(self, indexes: tuple):
        if (indexes[0] > 0 and indexes[1] > 0) and (indexes[1] < self.size - 1 and indexes[0] < self.size - 1):
            return True

        return False
