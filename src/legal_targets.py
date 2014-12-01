"""
  This file exports a method that generates all legal usages of an effect
  given a board.

  Targets are card names, not specific cards.
"""

import itertools

# Returns a list of tuples. Each tuple is a legal set of targets. In the event
# that no targets should be passed, the result is [()]
def generate_legal_targets(board, effect):
  fn = {
     1: _generate_legal_discard_cards,
     2: _no_targets,
     3: _no_targets,
     4: _no_targets,
     5: _no_targets,
     6: _generate_legal_banish_card_from_hand,
     7: _generate_legal_banish_card_from_center,
     8: _generate_legal_banish_card_from_discard,
     9: _generate_legal_defeat_monster,
    10: _no_targets,
    11: _generate_legal_acquire_hero,
    12: _no_targets,
    13: _no_targets,
    14: _generate_legal_banish_for_additional_turn,
    15: _no_targets,
    16: _no_targets,
    17: _no_targets,
    18: _no_targets,
    19: _no_targets,
    20: _generate_legal_put_acquired_mechana_construct_into_play,
    21: _no_targets,
    22: _no_targets,
    23: _no_targets,
    24: _no_targets,
    25: _no_targets,
    26: _generate_legal_copy_hero,
    27: _generate_legal_acquire_or_defeat_anything
  }[effect.effect_index]

  return fn(board, effect.param)

def _get_cards_from_hand(board):
  return [card.name for card in board.current_player().hand]

def _get_cards_from_center(board):
  return [card.name for card in board.center]

def _get_cards_from_discard(board):
  return [card.name for card in board.current_player().discard]

def _no_targets(board, param):
  return [()]

def _generate_legal_discard_cards(board, param):
  # all ways to discard param cards from a player's hand
  return list(itertools.combinations(_get_cards_from_hand(board), param))

def _generate_legal_banish_card_from_hand(board, param):
  return list(itertools.combinations(_get_cards_from_hand(board), param))

def _generate_legal_banish_card_from_center(board, param):
  return list(itertools.combinations(_get_cards_from_center(board), param))

def _generate_legal_banish_card_from_discard(board, param):
  return list(itertools.combinations(_get_cards_from_discard(board), param))

def _generate_legal_defeat_monster(board, param):
  # All monsters in the center (including the Cultist) with cost <= param
  return [(card.name,) for card in board.center
        if card.is_monster() and card.cost <= param] + \
    ([("Cultist",)] if param >= 2 else [])

def generate_legal_banish_for_additional_turn(board, param):
  CARD_NAME = "Tablet of Time's Dawn"
  assert any(card.name == CARD_NAME
    for card in board.current_player().constructs)

  return [(CARD_NAME,)]

def _generate_legal_put_acquired_mechana_construct_into_play(board, param):
  return [card.name for card in board.current_player().acquired_cards
    if board.current_player.considers_card_mechana_Construct(card)]

def _generate_legal_copy_hero(board, param):
  return [card.name for card in board.current_player().played_cards
    if card.is_hero()]

def _generate_legal_acquire_or_defeat_anything(board, param):
  ret = [("Cultist",)]
  if board.mystics > 0:
    ret.append(("Mystic",))
  if board.heavy > 0:
    ret.append(("Heavy Infantry",))

  ret.extend(_get_cards_from_center(board))
  return ret

