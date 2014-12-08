"""
  Strategy that revolves around deck control and drawing lifebound cards over
  and over again to gain honor from them (e.g. Flytrap Witch and Lifebound Initiate).
"""

from evaluating_strategy import EvaluatingStrategy

TAG = "lifebound"
CONFIG_PATH = "input/strategies/lifebound.txt"

# TODO(ddoucet): this should be configurable in file
OPTIMAL_DECK_RUNES = 12
OPTIMAL_DECK_POWER = 7

class LifeboundStrategy(EvaluatingStrategy):
  def __init__(self, player_index, num_players, card_dictionary):
    return super(LifeboundStrategy, self).__init__(
      TAG, player_index, num_players, card_dictionary, CONFIG_PATH,
      OPTIMAL_DECK_RUNES, OPTIMAL_DECK_POWER)

  # Defines the order in which we play cards. Returns None if no moves are "play"
  #
  # TODO(ddoucet): this ordering of moves doesn't benefit Arbiter of the Precipice
  # so that card isn't included in the valuations, which is silly.
  def _choose_nonbanish_play_move(self, board, legal_moves):
    # Play any cards that don't banish things.
    BANISH_FROM_HAND = 6
    BANISH_FROM_DISCARD = 8

    plays = [move for move in legal_moves
      if move.move_type == "play" and \
        move.targets is not None and \
        BANISH_FROM_HAND not in move.targets and \
        BANISH_FROM_DISCARD not in move.targets]

    # Play Druids of the Stone Circle first if we have that.
    druids = [move for move in plays if move.card_name == "Druids of the Stone Circle"]
    if len(druids) > 0:
      DRUID_EFFECT = 11

      return self._target_of_most_value(board, druids, DRUID_EFFECT)

    # Play any cards that aren't ones we want to play last.
    # Runic Lycanthrope gives us power for having played a Lifebound hero, so we
    # want to play it last (to give us a better chance of having played one). 
    ending_cards = ["Runic Lycanthrope", "Twofold Askara"]

    plays_without_ending = [move for move in plays if move.card_name not in ending_cards]
    if len(plays_without_ending) > 0:
      # TODO(ddoucet): things like banish from center should banish stuff we dislike
      # not things we like :P
      # same with discard
      return plays_without_ending[0]

    runic = [move for move in plays if move.card_name == "Runic Lycanthrope"]
    if len(runic) > 0:
      return runic[0]

    twofold = [move for move in plays if move.card_name == "Twofold Askara"]

    # Pick the target of most value.
    # TODO(ddoucet): This is technically not correct but meh.
    if len(twofold) > 0:
      TWOFOLD_EFFECT = 26
      return self._target_of_most_value(board, twofold, TWOFOLD_EFFECT)

    # No moves we want to play.
    return None

  def _choose_move(self, board, legal_moves):
    # TODO(ddoucet): refactor this into a pipeline of move selectors where a
    # node returns None if no move of that type can be made.
    # Better to do that after it's all working, though, I think.

    # Activate any constructs that aren't the Yggdrasil Staff (runes -> honor).
    activates = [move for move in legal_moves
      if move.move_type == "activate" and move.card_name != "Yggdrasil Staff"]
    if len(activates) > 0:
      return activates[0]

    play_move = self._choose_nonbanish_play_move(board, legal_moves)
    if play_move is not None:
      return play_move

    # If we can activate the Yggdrasil staff, we can convert 4 runes to 3 honor,
    # so we want to only acquire things that we value higher than that.
    # If we don't have the Yggdrasil staff, we can just acquire the best card.
    # TODO(ddoucet): we should value things based on deck cycling and turns left
    can_activate_yggdrasil = any(move.move_type == "activate" and \
        move.card_name == "Yggdrasil Staff"
      for move in legal_moves)
    acquire_threshold = 3.0 if can_activate_yggdrasil else 0.1

    acquire = self._acquire_of_most_value(board, legal_moves, acquire_threshold)
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
    return self._banish_card_of_least_value(board, legal_moves)

