"""
  Base class for strategies that actually do move evaluation. For now, it
  provides support for the following:

    * loading the configuration values
    * choosing an acquisition of a card of most value (optionally above a threshold)
    * banishing a card below a given threshold

  The config file doesn't need to specify every card. Any card not included will
  be given a default value of 0. We consider an effect that gives N honor worth
  value N. Other cards are valued in relation to that.

  The format of the config file is as follows:

    TODO(ddoucet)
"""

from legal_move_based_strategy import LegalMoveBasedStrategy, argmax, argmin
import src.input.files as files

class EvaluatingStrategy(LegalMoveBasedStrategy):
  def __init__(self, tag, player_index, num_players, card_dictionary, config_path):
    super(EvaluatingStrategy, self).__init__(tag, player_index, num_players, card_dictionary)

    self.card_name_to_value = defaultdict(float, files.read_kvp_file(config_path, float))

    assert all(card_dictionary.find_card(card_name) is not None
      for card_name in self.card_name_to_value.keys())

  def _card_name_to_value(self, card_name):
    # This could be overrided in subclasses to do more interesting logic.
    return self.card_name_to_value[card_name]

  # Returns the acquire move of most value, or None. Takes an optional threshold.
  def _acquire_of_most_value(self, legal_moves, threshold=0.0)
    def acquire_value(move):
      return threshold - 1 if move.move_type != "acquire" \
        else self.card_name_to_value[move.card_name]

    best_move_index = argmax([acquire_value(move) for move in legal_moves])
    best_move = legal_moves[best_move_index]

    return None if acquire_value(best_move) < threshold else best_move

  # Return the banish move of least value, or None. Takes an optional threshold
  # which is the highest value it will consider banishing.
  # The default threshold is 0.0 (which is the minimum value of a card).
  def _banish_card_of_least_value(self, legal_moves, threshold=0.0):
    BANISH_FROM_HAND = 6
    BANISH_FROM_DISCARD = 8

    def banish_value(effect_index, move):
      if move.move_type != "play" or effect_index not in move.targets:
        return threshold + 1

      return self.card_name_to_value[move.card_name]

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

    return None if banish_value(best_banish_from_hand) > threshold else best_banish_from_hand

