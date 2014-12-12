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
    if not card.is_monster() and board.current_player().can_acquire_card(card):
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
    # set for effect j.
    products = list(itertools.product(*effect_target_sets))

    # Convert those to the dictionaries that moves expects (effect index: target set)
    if products != []:
      # If products is [] that means that at least one of the effects didn't have
      # any legal targets, or it couldn't be activated at this time.
      for product in products:
        target_sets.extend(create_target_sets(board, card, effect_set, product))

  return target_sets

def create_target_sets(board, current_card, effect_set, product):
  DEFEAT_MONSTER = 9
  ACQUIRE_OR_DEFEAT_ANYTHING = 27
  COPY_HERO = 26

  # In the case of defeating a monster or copying a hero, a child card will
  # need targets. This method returns that card.
  def get_child_or_none(effect_index, targets):
    if effect_index == DEFEAT_MONSTER or effect_index == COPY_HERO:
      assert len(targets) == 1
      return board.card_dictionary.find_card(targets[0])
    elif effect_index == ACQUIRE_OR_DEFEAT_ANYTHING:
      assert len(targets) == 1
      card = board.card_dictionary.find_card(targets[0])

      return card if card.is_monster() else None

    return None

  # Returns a list of list of tuples (effect_index, targets)
  def find_child_targets(effect_index, targets):
    child = get_child_or_none(effect_index, targets)
    if child is None:
      return [[(effect_index, targets)]]

    target_sets = _generate_target_sets_for_card(board, child)

    # target_sets is a list of dicts
    target_set_tuples = [[(key, target_set[key]) for key in target_set.keys()]
      for target_set in target_sets
        if all(current_card.name not in target_set[key] for key in target_set.keys())]

    return [[(effect_index, targets)] + target_set_tuple
      for target_set_tuple in target_set_tuples]

  # We have to add some extra logic for the cases like arha templar or twofold
  # askara, which require some extra targets.
  child_targets = [find_child_targets(effect_set[i].effect_index, product[i])
    for i in xrange(len(effect_set))]

  products = list(itertools.product(*child_targets))

  return [{effect_index: targets
            for L in product
              for effect_index, targets in L}
        for product in products]

