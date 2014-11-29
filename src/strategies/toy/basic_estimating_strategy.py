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
  def __init__(self, player_index, num_players, card_dictionary):
    super(BasicEstimatingStrategy, self).__init__(TAG, player_index, num_players, card_dictionary)
    def make_metric_tracker():
      return MetricTracker(num_players * Board.HONOR_PER_PLAYER)

    self.my_tracker = make_metric_tracker()

    self.opponent_trackers = defaultdict(make_metric_tracker)

  def play_turn(self, board, opponents_previous_moves):
    self._execute_turn(board)

  def choose_construct_for_discard(self, board):
    assert len(board.players[self.player_index].constructs) == 0

    raise Exception("I don't have any constructs in play. " +
      "Why am I being asked to discard one?")

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

  def me_acquired_card(self, card):
    self.my_tracker.update_acquired_card(card)

  def opponent_acquired_card(self, opponent_index, card):
    self.opponent_trackers[opponent_index].update_acquired_card(card)

  def me_banished_from_deck(self, card):
    self.my_tracker.update_banished_card_from_deck(card)

  def opponent_banished_from_deck(self, opponent_index, card):
    self.opponent_trackers[opponent_index].update_banished_card_from_deck(card)

  def round_finished(self, board):
    self._update_estimates(board)
    self.log("Estimates: %s" % self.my_tracker.metrics)
    self.log("Honor: %d cards, %d tokens = %d total" % \
      (self.my_tracker.metrics['honor-in-cards'], \
       self.my_tracker.metrics['honor-in-tokens'], \
       self.my_tracker.metrics['honor-total']))

  def _update_estimates(self, board):
    player = board.current_player()
    honor = player.honor
    remaining = board.honor_remaining

    self.my_tracker.update_honor(honor, remaining)

    for player in board.other_players():
      honor = player.honor
      self.opponent_trackers[player.player_index].update_honor(honor, remaining)
