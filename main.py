import logging

from game_server import GameServer
from player import Player


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

gs = GameServer('127.0.0.1', 65432)

gs.wait_for_players()
