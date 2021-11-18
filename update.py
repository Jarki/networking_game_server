from enum import Enum


class UpdateTypes(Enum):
    GAME_UPDATE = 0
    MESSAGE_UPDATE = 1


class Update:
    def __init__(self, message, player, _type: UpdateTypes = UpdateTypes.GAME_UPDATE):
        if type(message) != bytes:
            message = str.encode(message)

        self.type = _type

        self.msg = message
        self.player = player
