"""
  Base class for strategies that actually do move evaluation. For now, it
  provides support for the following:

    * loading the configuration values
    * choosing an acquisition of a card of most value (optionally above a threshold)
    * banishing a card below a given threshold

  The config file doesn't need to specify every card. Any card not included will
  be given a default value of 0. We consider an effect that gives N honor worth
  value N. Other cards are valued in relation to that.

  The format of the config file is a series of lines of the form:

    card_name:float_value
"""

from collections import defaultdict
from legal_move_based_strategy import LegalMoveBasedStrategy, argmax, argmin
import src.input.files as files

class EvaluatingStrategy(LegalMoveBasedStrategy):
  def __init__(self, tag, player_index, num_players, card_dictionary, config_path,
               optimal_runes, optimal_power):
    super(EvaluatingStrategy, self).__init__(tag, player_index, num_players, card_dictionary)

    self.card_name_to_value = defaultdict(float, files.read_kvp_file(config_path, float))
    self.optimal_runes = optimal_runes
    self.optimal_power = optimal_power

    assert all(card_dictionary.find_card(card_name) is not None
      for card_name in self.card_name_to_value.keys())

  def _total_deck_runes(self, board):
    GAIN_RUNES_EFFECT = 3
    all_cards = board.players[self.player_index].all_cards()
    gain_rune_params = [card.get_effect_param(GAIN_RUNES_EFFECT) for card in all_cards]

    return sum(param for param in gain_rune_params if param is not None)

  def _total_deck_power(self, board):
    GAIN_POWER_EFFECT = 5
    all_cards = board.players[self.player_index].all_cards()
    gain_power_params = [card.get_effect_param(GAIN_POWER_EFFECT) for card in all_cards]

    return sum(param for param in gain_power_params if param is not None)

  def _card_name_to_value(self, card_name):
    # This could be overrided in subclasses to do more interesting logic.
    return self.card_name_to_value[card_name]

  # Returns the acquire move of most value, or None. Takes an optional threshold.
  def _acquire_of_most_value(self, board, legal_moves, threshold=0.0):
    def acquire_value(move):
      if move.move_type != "acquire":
        return threshold - 1
      elif move.card_name == "Mystic" and self._total_deck_runes(board) >= self.optimal_runes:
        return threshold - 1
      elif move.card_name == "Heavy Infantry" and self._total_deck_power(board) >= self.optimal_power:
        return threshold - 1

      return self._card_name_to_value(move.card_name)

    best_move_index = argmax([acquire_value(move) for move in legal_moves])
    best_move = legal_moves[best_move_index]

    return None if acquire_value(best_move) < threshold else best_move

  def _target_of_most_value(self, board, legal_moves, target_index):
    index = argmax([self._card_name_to_value(move.targets[target_index])
      for move in legal_moves])
    return legal_moves[index]

  # Return the banish move of least value, or None. Takes an optional threshold
  # which is the highest value it will consider banishing.
  # The default threshold is 0.0 (which is the minimum value of a card).
  def _banish_card_of_least_value(self, board, legal_moves, threshold=0.0):
    BANISH_FROM_HAND = 6
    BANISH_FROM_DISCARD = 8

    def banish_value(effect_index, move):
      if move.move_type != "play" or move.targets is None or effect_index not in move.targets:
        return threshold + 1

      return self._card_name_to_value(move.card_name)

    # First check for banishes from discard.
    best_banish_from_discard_index = argmin([banish_value(BANISH_FROM_DISCARD, move)
      for move in legal_moves])

    best_banish_from_discard = legal_moves[best_banish_from_discard_index]
    if banish_value(BANISH_FROM_DISCARD, best_banish_from_discard) <= threshold:
      return best_banish_from_discard

    # Now check for banishes from hand.
    best_banish_from_hand_index = argmin([banish_value(BANISH_FROM_HAND, move)
      for move in legal_moves])

    best_banish_from_hand = legal_moves[best_banish_from_hand_index]

    return None if banish_value(BANISH_FROM_HAND, best_banish_from_hand) > threshold \
      else best_banish_from_hand

