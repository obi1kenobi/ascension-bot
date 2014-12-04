"""
  This file exports a method that generates all legal usages of an effect
  given a board.

  Targets are card names, not specific cards.
"""

import itertools

# Returns a list of tuples. Each tuple is a legal set of targets. In the event
# that no targets should be passed, the result is [()]. If the card cannot be
# activated, the result is [].
# current_card is the card activating the effect. We need this in the case of
# trying to banish a card from the center (defeating a monster cannot cause that
# monster to banish itself).
def generate_legal_targets(board, current_card, effect):
  fn = {
     1: _generate_legal_discard_cards,
     2: _no_targets,
     3: _generate_legal_gain_runes,
     4: _no_targets,
     5: _generate_legal_gain_power,
     6: _generate_legal_banish_card_from_hand,
     7: _generate_legal_banish_card_from_center,
     8: _generate_legal_banish_card_from_discard,
     9: _generate_legal_defeat_monster,
    10: _no_targets,
    11: _generate_legal_acquire_hero,
    12: _no_targets,
    13: _generate_legal_draw_for_mechana_construct,
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

  return fn(board, current_card, effect.param)

def _get_cards_from_hand(board, card):
  legal_hand_cards = [c for c in board.current_player().hand
    if card != c]
  return [card.name for card in legal_hand_cards]

def _get_cards_from_center(board, card):
  legal_center_cards = [c for c in board.center
    if card != c]
  return [card.name for card in legal_center_cards]

def _get_cards_from_discard(board):
  return [card.name for card in board.current_player().discard]

def _no_targets(board, current_card, param):
  return [()]

def _generate_legal_gain_runes(board, current_card, param):
  return [()] if board.current_player().runes_remaining + param >= 0 else []

def _generate_legal_gain_power(board, current_card, param):
  return [()] if board.current_player().power_remaining + param >= 0 else []

def _generate_legal_discard_cards(board, current_card, param):
  # all ways to discard param cards from a player's hand
  return list(itertools.combinations(_get_cards_from_hand(board, current_card), param))

def _generate_legal_banish_card_from_hand(board, current_card, param):
  return list(itertools.combinations(_get_cards_from_hand(board, current_card), param))

def _generate_legal_banish_card_from_center(board, current_card, param):
  legal_cards = [card_name for card_name in _get_cards_from_center(board, current_card)
    if card_name != "Avatar of the Fallen"]

  return list(itertools.combinations(legal_cards, param))

def _generate_legal_banish_card_from_discard(board, current_card, param):
  return list(itertools.combinations(_get_cards_from_discard(board), param))

def _generate_legal_acquire_hero(board, current_card, param):
  # All heroes in the center (including Mystics and Heavies) with cost <= param
  return [(card.name,) for card in board.center
      if card.is_hero() and card.cost <= param] + \
    ([("Mystic",)] if param >= 3 else []) + \
    ([("Heavy Infantry",)] if param >= 2 else [])

def _generate_legal_defeat_monster(board, current_card, param):
  # All monsters in the center (including the Cultist) with cost <= param
  return [(card.name,) for card in board.center
      if card.is_monster() and card.cost <= param] + \
    ([("Cultist",)] if param >= 2 else [])

def _generate_legal_banish_for_additional_turn(board, current_card, param):
  CARD_NAME = "Tablet of Time's Dawn"
  assert any(card.name == CARD_NAME
    for card in board.current_player().constructs)

  return [(CARD_NAME,)]

def _generate_legal_draw_for_mechana_construct(board, current_card, param):
  return [()] if board.current_player().has_played_mechana_construct() else []

def _generate_legal_put_acquired_mechana_construct_into_play(board, current_card, param):
  return [(card.name,) for card in board.current_player().acquired_cards
    if board.current_player().considers_card_mechana_construct(card)]

def _generate_legal_copy_hero(board, current_card, param):
  return [(card.name,) for card in board.current_player().played_cards
    if card.is_hero() and card != current_card]

def _generate_legal_acquire_or_defeat_anything(board, current_card, param):
  ret = [("Cultist",)]
  if board.mystics > 0:
    ret.append(("Mystic",))
  if board.heavy > 0:
    ret.append(("Heavy Infantry",))

  ret.extend((card_name,) for card_name in _get_cards_from_center(board, current_card))
  return ret

