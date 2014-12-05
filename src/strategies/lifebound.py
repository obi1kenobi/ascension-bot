"""
  Strategy that revolves around deck control and drawing lifebound cards over
  and over again to gain honor from them (e.g. Flytrap Witch and Lifebound Initiate).
"""

from evaluating_strategy import EvaluatingStrategy

TAG = "lifebound"
CONFIG_PATH = "input/strategies/lifebound.txt"

class LifeboundStrategy(EvaluatingStrategy):
  def __init__(self, player_index, num_players, card_dictionary):
    return super(LifeboundStrategy).__init__(
      TAG, player_index, num_players, card_dictionary, CONFIG_PATH)

  def _choose_move(self, board, legal_moves):
    BANISH_FROM_HAND = 6
    BANISH_FROM_DISCARD = 8

    # Activate any constructs that aren't the Yggdrasil Staff (runes -> honor).
    activates = [move for move in legal_moves
      if move.move_type == "activate" and move.card_name != "Yggdrasil Staff"]
    if len(activates) > 0:
      return activates[0]

    # Play any cards that don't banish things.
    plays = [move for move in legal_moves
      if move.move_type == "play" and \
        BANISH_FROM_HAND not in move.targets and \
        BANISH_FROM_DISCARD not in move.targets]
    if len(plays) > 0:
      # TODO(ddoucet): do any cards in this strategy involve targeted effectrs?
      # if so we should probably be intelligent about which targets we choose
      return plays[0]

    # TODO(ddoucet): things like banish from center should banish stuff we dislike
    # not things we like :P
    # same with discard

    # TODO(ddoucet): this ordering of moves doesn't benefit Arbiter of the Precipice
    # so that card isn't included in the valuations, which is silly.

    # If we can activate the Yggdrasil staff, we can convert 4 runes to 3 honor,
    # so we want to only acquire things that we value higher than that.
    # If we don't have the Yggdrasil staff, we can just acquire the best card.
    # TODO(ddoucet): we should value things based on deck cycling and turns left
    can_activate_yggdrasil = any(move.move_type == "activate" and \
        move.card_name == "Yggdrasil Staff"
      for move in legal_moves)
    acquire_threshold = 3.0 if can_activate_yggdrasil else 0.1

    acquire = self._acquire_of_most_value(legal_moves, acquire_threshold)
    if acquire is not None:
      return acquire

    # If we have runes and can activate the Yggdrasil Staff, it means there
    # wasn't a better use of our runes, so do that.
    yggdrasil_activates = [move for move in legal_moves
      if move.move_type == "activate" and move.card_name == "Yggdrasil Staff"]

    # First check if we can activate the one that gives us honor. Otherwise, if
    # there are any activates at all, activate it (to get the power).
    if len(yggdrasil_activates) > 0:
      GAIN_HONOR_EFFECT = 4
      honor_yggdrasils = [move for move in yggdrasil_activates
        if GAIN_HONOR_EFFECT in move.targets]

      if len(honor_yggdrasils) > 0:
        return honor_yggdrasils[0]
      else:
        return yggdrasil_activates[0]

    # Defeat the monsters of highest value if we can.
    defeats = [move for move in legal_moves if move.move_type == "defeat"]
    if len(defeats) > 0:
      return self._move_worth_most_honor(defeats)

    # If we can banish any cards we don't want, do that.
    return self._banish_card_of_least_value(moves)

