"""
  Strategy that revolves around 
"""

from evaluating_strategy import EvaluatingStrategy

TAG = "mechana"
CONFIG_PATH = "strategies/mechana.txt"

# TODO(ddoucet): this should be configurable in file
OPTIMAL_DECK_RUNES = 18
OPTIMAL_DECK_POWER = 0

class MechanaStrategy(EvaluatingStrategy):
  def __init__(self, player_index, num_players, card_dictionary):
    return super(MechanaStrategy, self).__init__(
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
        (move.targets is None or \
        (move.targets is not None and \
        BANISH_FROM_HAND not in move.targets and \
        BANISH_FROM_DISCARD not in move.targets))]

    # Play any cards that aren't ones we want to play last.
    # Runic Lycanthrope gives us power for having played a Lifebound hero, so we
    # want to play it last (to give us a better chance of having played one). 
    ending_cards = ["Twofold Askara"]

    plays_without_ending = [move for move in plays if move.card_name not in ending_cards]
    if len(plays_without_ending) > 0:
      # TODO(ddoucet): things like banish from center should banish stuff we dislike
      # not things we like :P
      # same with discard
      return plays_without_ending[0]

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
    # We only activate the Tablet of Time's Dawn if we have at least 6 constructs.
    # This is a reasonable heuristic for when we'll likely have a strong turn.
    num_constructs = len(board.current_player().constructs)
    activates = [move for move in legal_moves
      if move.move_type == "activate" and move.card_name != "Yggdrasil Staff" and \
        (move.card_name != "Tablet of Time's Dawn" or num_constructs >= 6)]
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
    acquire_threshold = 3.1 if can_activate_yggdrasil else 0.1

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

