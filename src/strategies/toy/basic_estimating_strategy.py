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
from src.moves import Move
from src.estimators.estimators import AverageEstimator, WeightedAverageEstimator, LimitedHorizonLinearFitEstimator
from collections import defaultdict

TAG = "basic_estimating"

GAIN_RUNES_EFFECT = 3
GAIN_HONOR_EFFECT = 4
GAIN_POWER_EFFECT = 5

class BasicEstimatingStrategy(Strategy):
  def __init__(self, player_index):
    super(BasicEstimatingStrategy, self).__init__(TAG, player_index)
    self.metrics = defaultdict(float)
    self.metrics['eff-deck-size'] = 10.0
    self.metrics['eff-hand-size'] = 5.0
    self.estimators = {
      'turns-remaining': LimitedHorizonLinearFitEstimator(10),
      'real-deck-size': WeightedAverageEstimator(0.8),
      'real-hand-size': AverageEstimator()
    }

  def _update_deck_size(self, card):
    eff_deck_size_increase = 1
    construct_types = {'Enlightened Construct', 'Void Construct', 'Mechana Construct', 'Lifebound Construct'}

    if card.card_type in construct_types:
      # constructs don't increase the effective deck size
      eff_deck_size_increase -= 1

    # TODO(predrag): Update effective deck size for 'draw card' effect cards

    # All-Seeing Eye's effect affects the hand size but not the deck size
    # to avoid double-counting

    self.metrics['eff-deck-size'] += eff_deck_size_increase

  def _update_hand_size(self, card):
    eff_hand_size_increase = 0

    # TODO(predrag): Switch to checking effects rather than hard-coding effects
    if card.name == "The All-Seeing Eye":
      eff_hand_size_increase += 1

    self.metrics['eff-hand-size'] += eff_hand_size_increase

  def _event_acquired_card(self, card):
    self._update_deck_size(card)
    self._update_hand_size(card)

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

    self.metrics['eff-deck-size'] += runes / 2

    self.metrics['real-hand-size'] = self.estimators['real-hand-size'].push(len(hand))

    # TODO(predrag): add tracking of real-deck-size

    for move in moves:
      self.play_move(board, move)

    for i in xrange(runes/2):
      self._event_acquired_card(board.card_dictionary.find_card("Heavy Infantry"))

  def _update_estimates(self, board):
    player = board.current_player()
    hand = player.get_hand()

    self.metrics['eff-deck-cycle-length'] = self.metrics['eff-deck-size'] / \
                                            self.metrics['eff-hand-size']

    honor_gained_in_last_turn = self.metrics['honor-remaining'] - board.honor_remaining
    self.metrics['honor-remaining'] = board.honor_remaining

    # < 0 if it's the first turn of the game
    # TODO(predrag): not entirely correct, add better logic
    if honor_gained_in_last_turn >= 0:
      self.metrics['temp-estimate-next-turn-honor-gained'] = \
        self.estimators['turns-remaining'].push(honor_gained_in_last_turn)
      self.metrics['turns-remaining'] = \
        self.estimators['turns-remaining'].estimate_turns_to_sum(board.honor_remaining)

  def play_turn(self, board, opponents_previous_moves):
    self._execute_turn(board)
    self._update_estimates(board)

    self.log("Estimates: %s" % self.metrics)
    self.log("Honor: %d" % board.current_player().honor)

  def choose_construct_for_discard(self, board):
    assert len(board.players[self.player_index].constructs) == 0

    raise Exception("I don't have any constructs in play. " +
      "Why am I being asked to discard one?")

