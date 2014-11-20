"""
  This is the class that wraps all strategies. Simply implement this and then
  plug it into main.py.
"""

VERBOSE = True

class Strategy(object):
  def __init__(self, tag, player_index):
    # TODO(ddoucet): colors for logging
    self.tag = tag
    self.player_index = player_index

  def log(self, msg):
    if VERBOSE:
      print "P%d %s: %s" % (self.player_index, self.tag, msg)

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

