"""
  This file exports a method that applies a simple effect (see
  card_decoder/cards.py) to a board (given that the board has a current player)
  given the targets (if necessary).

  Many effects have different requirements and will raise exceptions if the
  requirements aren't met.

  Targets are card names, not specific cards.
"""

import random
from events import raise_strategy_card_events, raise_strategy_card_events_for_player

def apply_simple_effect(board, effect, targets):
  # TODO(ddoucet): setup logging for server and log effect name,param here (str(effect)?)
  fn = {
     1: _discard_cards,
     2: _draw_cards,
     3: _gain_runes,
     4: _gain_honor,
     5: _gain_power,
     6: _banish_card_from_hand,
     7: _banish_card_from_center,
     8: _banish_card_from_discard,
     9: _defeat_monster,
    10: _pay_less_runes_toward_mechana_construct,
    11: _acquire_hero,
    12: _gain_honor_for_lifebound_hero,
    13: _draw_card_for_mechana_construct,
    14: _banish_for_additional_turn,
    15: _pay_less_runes_toward_construct,
    16: _gain_honor_for_defeating_monster,
    17: _draw_for_two_or_more_constructs,
    18: _gain_honor_per_faction_of_constructs,
    19: _each_opponent_destroys_construct,
    20: _put_acquired_mechana_construct_into_play,
    21: _treat_all_constructs_as_mechana_constructs,
    22: _take_random_card_from_each_opponent,
    23: _gain_power_if_lifebound_hero_played,
    24: _opponents_destroy_all_but_one_construct,
    25: _gain_power_for_each_mechana_construct,
    26: _copy_hero,
    27: _acquire_or_defeat_anything
  }[effect.effect_index]

  fn(board, effect.param, targets[effect.effect_index], targets)

def _discard_cards(board, param, my_targets, all_targets):
  assert param == len(my_targets), "Expected %d targets; got %s" % (
    param, str(my_targets))

  for card_name in my_targets:
    # Raises an exception if the card isn't in the player's hand
    board.current_player().discard_card()

def _draw_cards(board, param, my_targets, all_targets):
  assert len(my_targets) == 0, "Expected no targets; got %s" % str(my_targets)

  for i in xrange(param):
    board.current_player().draw_card()

def _gain_runes(board, param, my_targets, all_targets):
  assert len(my_targets) == 0, "Expected no targets; got %s" % str(my_targets)

  board.current_player().runes_remaining += param

  # Some cards cost runes to play; the effect is in the form of gaining
  # negative runes
  assert board.current_player().runes_remaining >= 0

def _gain_honor(board, param, my_targets, all_targets):
  assert len(my_targets) == 0, "Expected no targets; got %s" % str(my_targets)
  assert param >= 0, "Effect should not give negative honor"

  board.give_honor(board.current_player(), param)

def _gain_power(board, param, my_targets, all_targets):
  assert len(my_targets) == 0, "Expected no targets; got %s" % str(my_targets)

  assert board.current_player().power_remaining + param >= 0, "Not enough power to play this card"

  board.current_player().power_remaining += param

def _banish_card_from_hand(board, param, my_targets, all_targets):
  assert param == len(my_targets), "Expected %d targets; got %s" % (
    param, str(my_targets))

  for card_name in my_targets:
    card = board.current_player().remove_card_from_hand(card_name)
    board.void.append(card)

    raise_strategy_card_events(board, 'banished_from_deck', card_name)

def _banish_card_from_center(board, param, my_targets, all_targets):
  assert param == len(my_targets), "Expected %d targets; got %s" % (
    param, str(my_targets))

  assert "Avatar of the Fallen" not in my_targets, "Cannot banish Avatar of the Fallen"

  for card_name in my_targets:
    card = board.remove_card_from_center(card_name)
    board.void.append(card)

    raise_strategy_card_events(board, 'banished_from_center', card_name)

def _banish_card_from_discard(board, param, my_targets, all_targets):
  assert param == len(my_targets), "Expected %d targets; got %s" % (
    param, str(my_targets))

  for card_name in my_targets:
    card = board.current_player().remove_card_from_discard(card_name)
    board.void.append(card)

    raise_strategy_card_events(board, 'banished_from_deck', card_name)

def _defeat_monster(board, param, my_targets, all_targets):
  assert len(my_targets) == 1, "Expected 1 target; got %s" % str(my_targets)

  card_name = my_targets[0]
  card = board.card_dictionary.find_card(card_name)

  assert card.card_type == "Monster", "Tried to defeat %s, which is not a monster" % (
    card.name)

  assert card.cost <= param, ("Can only use this effect to defeat monsters up to %d power" +
    " (%s costs %d power)" % (param, card.name, card.cost))

  board.current_player().power_remaining += card.cost
  Move("defeat", card_name, all_targets, all_targets).apply_to_board(board, False)

def _pay_less_runes_toward_mechana_construct(board, param, my_targets, all_targets):
  assert len(my_targets) == 0, "Expected no targets; got %s" % str(my_targets)

  board.current_player().runes_toward_mechana_constructs += param

def _acquire_hero(board, param, my_targets, all_targets):
  assert len(my_targets) == 1, "Expected 1 target; got %s" % str(my_targets)

  card_name = my_targets[0]
  card = board.card_dictionary.find_card(card_name)

  assert "Hero" in card.card_type, "Tried to acquire %s, which is not a hero" % (
    card.name)

  assert card.cost <= param, ("Can only use this effect to acquire heros up to %d runes" +
    " (%s costs %d runes)" % (param, card.name, card.cost))

  board.current_player().runes_remaining += card.cost
  Move("acquire", card_name, all_targets, all_targets).apply_to_board(board, False)

def _gain_honor_for_lifebound_hero(board, param, my_targets, all_targets):
  assert len(my_targets) == 0, "Expected no targets; got %s" % str(my_targets)

  board.current_player().honor_for_lifebound_hero += param

def _draw_card_for_mechana_construct(board, param, my_targets, all_targets):
  assert len(my_targets) == 0, "Expected no targets; got %s" % str(my_targets)

  if board.current_player().has_played_mechana_construct:
    board.current_player().draw_card()

def _banish_for_additional_turn(board, param, my_targets, all_targets):
  assert len(my_targets) == 1, "Expected 1 target; got %s" % str(my_targets)

  card_name = my_targets[0]
  assert card_name == "Tablet of Time's Dawn"

  board.current_player().should_take_additional_turn = True
  card = board.current_player().remove_card_from_constructs(card_name)
  board.void.append(card)

  raise_strategy_card_events(board, 'banished_from_deck', card_name)

  # we know the only card with this effect is the Tablet of Time's Dawn
  # and it's a construct
  assert card.is_construct()

  raise_strategy_card_events(board, 'construct_removed', card_name)

def _pay_less_runes_toward_construct(board, param, my_targets, all_targets):
  assert len(my_targets) == 0, "Expected 0 targets; got %s" % str(my_targets)

  board.current_player().runes_toward_constructs += param

def _gain_honor_for_defeating_monster(board, param, my_targets, all_targets):
  assert len(my_targets) == 0, "Expected 0 targets; got %s" % str(my_targets)

  board.give_honor(board.current_player(), param)

def _draw_for_two_or_more_constructs(board, param, my_targets, all_targets):
  assert len(my_targets) == 0, "Expected 0 targets; got %s" % str(my_targets)

  if len(board.current_player().constructs) >= 2:
    board.current_player().draw_card()

def _gain_honor_per_faction_of_constructs(board, param, my_targets, all_targets):
  assert len(my_targets) == 0, "Expected 0 targets; got %s" % str(my_targets)

  construct_types = set(card.name for card in board.current_player().constructs)
  board.give_honor(board.current_player(), param * len(construct_type))

def _get_opponent_indices(board):
  return [i for i in xrange(len(board.players))
    if i != board.current_player_index]

def _destroy_opponent_construct(board, opponent_index):
  opponent = board.players[opponent_index]

  card_name = board.strategies[opponent_index].choose_construct_for_discard()
  card = opponent.remove_card_from_constructs(card_name)
  opponent.discard.append(card)

  raise_strategy_card_events_for_player(board, opponent_index, 'construct_removed', card_name)

def _each_opponent_destroys_construct(board, param, my_targets, all_targets):
  assert len(my_targets) == 0, "Expected 0 targets; got %s" % str(my_targets)

  opponent_indices = _get_opponent_indices(board)

  for opponent_index in opponent_indices:
    opponent = board.players[opponent_index]
    if len(opponent.constructs) > 0:
      _destroy_opponent_construct(board, opponent_index)

def _put_acquired_mechana_construct_into_play(board, param, my_targets, all_targets):
  assert len(my_targets) == 1, "Expected 1 target; got %s" % str(my_targets)

  card_name = my_targets[0]
  card = board.current_player().remove_card_from_acquired_cards(card_name)
  board.current_player().constructs.append(card)

def _treat_all_constructs_as_mechana_constructs(board, param, my_targets, all_targets):
  # This purposefully does nothing. Its effect is used when other effects might
  # need a mechana construct; the player simply checks if the associated card
  # is in the player's constructs
  pass

def _take_random_card_from_each_opponent(board, param, my_targets, all_targets):
  assert len(my_targets) == 0, "Expected no targets; got %s" % str(my_targets)
  opponent_indices = _get_opponent_indices(board)

  for opponent_index in opponent_indices:
    opponent = board.players[opponent_index]
    card_name = random.choice(opponent.hand).name
    card = opponent.remove_card_from_hand(card_name)

    raise_strategy_card_events_for_player(board, opponent_index, 'banished_from_deck', card_name)

    board.current_player.hand.append(card)

    raise_strategy_card_events(board, 'acquired_card', card_name)

def _gain_power_if_lifebound_hero_played(board, param, my_targets, all_targets):
  assert len(my_targets) == 0, "Expected no targets; got %s" % str(my_targets)

  if any(card.card_type == "Lifebound Hero"
      for card in board.current_player().played_cards):
    board.current_player().power_remaining += param

def _opponents_destroy_all_but_one_construct(board, param, my_targets, all_targets):
  assert len(my_targets) == 0, "Expected no targets; got %s" % str(my_targets)

  opponent_indices = _get_opponent_indices(board)

  for opponent_index in opponent_indices:
    opponent = board.players[opponent_index]
    while len(opponent.constructs) > 1:
      # TECHNICALLY this isn't actually quite correct but I feel like this
      # simplification is close enough to correct that it doesn't matter.
      _destroy_opponent_construct(board, opponent_index)

def _gain_power_for_each_mechana_construct(board, param, my_targets, all_targets):
  assert len(my_targets) == 0, "Expected no targets; got %s" % str(my_targets)

  num_mechana_constructs = sum(1 for card in board.current_player().constructs
    if board.current_player().considers_card_mechana_construct(card))

  board.current_player().power_remaining += num_mechana_constructs * param

def _copy_hero(board, param, my_targets, all_targets):
  assert len(my_targets) == 1, "Expected 1 target; got %s" % str(my_targets)

  card_name = my_targets[0]

  assert card_name in board.current_player().played_cards, ("Tried to copy" +
    " the effect of a card that wasn't played")

  card = board.current_player().remove_card_from_played_cards(card_name)
  board.current_player().hand.append(card)
  Move("play", card_name, all_targets).apply_to_board(board, False)

def _acquire_or_defeat_anything(board, param, my_targets, all_targets):
  assert len(my_targets) == 1, "Expected 1 target; got %s" % str(my_targets)

  card_name = my_targets[0]
  card = board.card_dictionary.find_card(card_name)

  if card.card_type == "Monster":
    # The param for _defeat_monster is the upper bound of cost that the effect
    # can defeat. In this case, we want anything so we give a very large upper
    # bound.
    _defeat_monster(board, 10000, my_targets)
  else:
    board.current_player().runes_remaining += card.cost
    Move("acquire", card_name, all_targets).apply_to_board(board, False)

