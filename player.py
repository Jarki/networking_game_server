class Player:
    def __init__(self, p_id=-1, nickname=""):
        self.p_id = p_id
        self.nickname = nickname

    def get_name(self):
        return self.nickname
