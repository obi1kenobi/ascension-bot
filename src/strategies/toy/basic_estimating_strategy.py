"""
  This strategy is a very simple test strategy used to show basic tracking of metrics.
  With respect to card play choices, it copies the BasicStrategy:

    On any given turn, do the following:
      1) Play all cards.
      2) Buy RUNES/2 heavy infantry.
      3) Kill the cultist POWER/2 times.

  Since we never buy anything that isn't simple, we never have to deal with
  specifying targets of effects.
"""

from ..strategy import Strategy
from src.board import Board
from src.moves import Move
from collections import defaultdict
from src.constants.effect_indexes import *
from src.estimators.metric_tracker import MetricTracker

TAG = "basic_estimating"

class BasicEstimatingStrategy(Strategy):
  def __init__(self, player_index, num_players):
    super(BasicEstimatingStrategy, self).__init__(TAG, player_index)
    def make_metric_tracker():
      t = MetricTracker()
      t.update_honor_remaining(num_players * Board.HONOR_PER_PLAYER)
      return t

    self.num_players = num_players
    self.my_tracker = make_metric_tracker()
    self.opponent_trackers = defaultdict(make_metric_tracker)

  def _execute_turn(self, board):
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

    # TODO(predrag): add tracking of real-deck-size, real-hand-size

    for move in moves:
      self.play_move(board, move)

    for i in xrange(runes/2):
      self.my_tracker.update_acquired_card(board.card_dictionary.find_card("Heavy Infantry"))

  def _update_estimates(self, board):
    player = board.current_player()
    hand = player.get_hand()

    honor_gained_this_round = self.my_tracker.metrics['honor-remaining'] - board.honor_remaining
    assert honor_gained_this_round >= 0

    self.my_tracker.update_honor_remaining(board.honor_remaining)
    self.my_tracker.update_honor_gained_this_round(honor_gained_this_round)

  def play_turn(self, board, opponents_previous_moves):
    self._execute_turn(board)
    self._update_estimates(board)

    self.log("Estimates: %s" % self.my_tracker.metrics)
    self.log("Honor: %d" % board.current_player().honor)

  def choose_construct_for_discard(self, board):
    assert len(board.players[self.player_index].constructs) == 0

    raise Exception("I don't have any constructs in play. " +
      "Why am I being asked to discard one?")

