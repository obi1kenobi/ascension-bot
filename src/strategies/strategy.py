"""
  This is the class that wraps all strategies. Simply implement this and then
  plug it into main.py.
"""

from .. import log

PLAYER_INDEX_TO_COLOR = {
  0: log.GREEN,
  1: log.BLUE
}


class Strategy(object):
  def __init__(self, tag, player_index):
    self.tag = tag
    self.player_index = player_index

    logger_name = "P%d %s" % (player_index, tag)
    color = PLAYER_INDEX_TO_COLOR[player_index]
    self.logger = log.create_logger(logger_name, color)

  def log(self, msg):
    self.logger.info(msg)

  # winner will either be str(index) or "tie"
  def log_end_game(self, winner):
    if winner == str(self.player_index):
      self.log("I won!")
    elif winner == "tie":
      self.log("We tied")
    else:
      self.log("I lost!")

  def play_move(self, board, move):
    self.log(str(move))
    move.apply_to_board(board)

  def play_turn(self, board):
    raise NotImplementedError('play_turn')

  def choose_construct_for_discard(self, board):
    raise NotImplementedError('choose_construct_for_discard')

