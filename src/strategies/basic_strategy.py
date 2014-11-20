"""
  This strategy is a very simple test strategy used for demonstrating that the
  server works.

    On any given turn, do the following:
      1) Play all cards.
      2) Buy RUNES/2 heavy infantry.
      3) Kill the cultist POWER/2 times.
 
  Since we never buy anything that isn't simple, we never have to deal with
  specifying targets of effects.
"""

from strategy import Strategy
from src.moves import Move

TAG = "Basic Strategy"

class BasicStrategy(Strategy):
  def __init__(self, player_index):
    super(BasicStrategy, self).__init__(TAG, player_index)

  def play_turn(self, board):
    assert board.current_player() == board.players[self.player_index]

    player = board.current_player()
    hand = player.get_hand()

    for card in hand:
      self.play_move(board, Move("play", card.name))

    runes = player.runes_remaining
    power = player.power_remaining
    self.log("Runes: %d, Power: %d" % (runes, power))

    moves = ([Move("acquire", "Heavy Infantry")] * (runes / 2) +
      [Move("defeat", "Cultist")] * (power / 2))

    for move in moves:
      self.play_move(board, move)

    self.log("Honor: %d" % player.honor)

  def choose_construct_for_discard(self, board):
    assert len(board.players[self.player_index].constructs) == 0

    raise Exception("I don't have any constructs in play. " +
      "Why am I being asked to discard one?")

