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

TAG = "basic"

GAIN_RUNES_EFFECT = 3
GAIN_HONOR_EFFECT = 4
GAIN_POWER_EFFECT = 5

class BasicStrategy(Strategy):
  def __init__(self, player_index, num_players, card_dictionary):
    super(BasicStrategy, self).__init__(TAG, player_index, num_players, card_dictionary)

  def play_turn(self, board, opponents_previous_moves):
    assert board.current_player() == board.players[self.player_index]

    player = board.current_player()
    hand = player.get_hand()

    targets = {GAIN_RUNES_EFFECT: [], GAIN_HONOR_EFFECT: [], GAIN_POWER_EFFECT: []}

    for card in hand:
      self.play_move(board, Move("play", card.name, targets))

    runes = player.runes_remaining
    power = player.power_remaining
    self.log("Runes: %d, Power: %d" % (runes, power))

    moves = ([Move("acquire", "Heavy Infantry", None)] * (runes / 2) +
      [Move("defeat", "Cultist", {GAIN_HONOR_EFFECT: []})] * (power / 2))

    for move in moves:
      self.play_move(board, move)

    self.log("Honor: %d (Total Honor: %d)" % (player.honor, player.compute_honor()))

  def choose_construct_for_discard(self, board):
    assert len(board.players[self.player_index].constructs) == 0

    raise Exception("I don't have any constructs in play. " +
      "Why am I being asked to discard one?")

