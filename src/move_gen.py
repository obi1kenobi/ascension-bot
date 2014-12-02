"""
  Generate a list of possible moves for the current player given a board state.
"""

import itertools
from moves import Move
from legal_targets import generate_legal_targets

def generate_moves(board):
  return (_generate_acquires(board) + _generate_defeats(board) +
    _generate_plays(board) + _generate_activates(board))

def _generate_acquires(board):
  card_names = []
  runes = board.current_player().runes_remaining

  if board.mystics > 0 and runes >= 3:
    card_names.append("Mystic")
  if board.heavy > 0 and runes >= 2:
    card_names.append("Heavy Infantry")

  for card in board.center:
    if not card.is_monster() and card.cost <= runes:
      card_names.append(card.name)

  return [Move("acquire", card_name, None) for card_name in card_names]

def _generate_defeats(board):
  GAIN_HONOR_EFFECT = 4

  card_name_target_tuples = []
  power = board.current_player().power_remaining

  if power >= 2:
    card_name_target_tuples.append(("Cultist", {GAIN_HONOR_EFFECT: ()}))

  for card in board.center:
    if card.is_monster() and card.cost <= power:
      for targets in _generate_target_sets_for_card(board, card):
        card_name_target_tuples.append((card.name, targets))

  return [Move("defeat", card_name, targets) for card_name, targets in card_name_target_tuples]

def _generate_plays(board):
  moves = []

  for card in board.current_player().hand:
    if card.is_construct():
      moves.append(Move("play", card.name, None))
    else:
      target_sets = _generate_target_sets_for_card(board, card)
      moves.extend([Move("play", card.name, targets) for targets in target_sets])

  return moves

def _generate_activates(board):
  legal_constructs = [card for card in board.current_player().constructs
    if board.current_player().can_activate_construct(card.name)]
  moves = []

  for card in legal_constructs:
    target_sets = _generate_target_sets_for_card(board, card)
    moves.extend([Move("activate", card.name, targets) for targets in target_sets])

  return moves

# For a given card, generate all legal target sets that can come from activating
# the effect of the card.
def _generate_target_sets_for_card(board, card):
  target_sets = []
  legal_effect_sets = card.generate_legal_effect_sets()

  for effect_set in legal_effect_sets:
    # Create a list of lists: list i corresponds to legal target sets for effect i
    effect_target_sets = [generate_legal_targets(board, card, effect) for effect in effect_set]

    # Use products to create sets so that in set i, element j corresponds to the target
    # sets for effect j
    products = list(itertools.product(*effect_target_sets))

    # Convert those to the dictionaries that Moves expects (effect index: target set)
    if products != []:
      # If products is [] that means that at least one of the effects didn't have
      # any legal targets, or it couldn't be activated at this time.
      target_sets.append({effect_set[j].effect_index: product[j]
        for product in products for j in xrange(len(effect_set))})

  return target_sets

