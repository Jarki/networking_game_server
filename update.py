class Update:
    def __init__(self, message, player):
        if type(message) != bytes:
            message = str.encode(message)

        self.msg = message
        self.player = player
