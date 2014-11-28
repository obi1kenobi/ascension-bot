"""
  Represents moves that a player can make. A move is one of several different
  types: acquiring a card, defeating a card, playing a card, or activating a
  construct.

  To construct a move, pass it a move_type, a card_name (what the move is
  acting on, e.g., what card is being acquired), and optionally targets if the
  move_type is play, activate, or defeat.

  Targets is either None (if the move type is acquire) or a dict mapping effect
  index to a list of card names. There are rules about which keys should exist
  in the dict. If the specific effect (note that some cards have more than one
  effect) is being used, it must include an entry, even if the entry maps to an
  empty list. This is important because some effects are optional, and some
  effects are chained (e.g., discard a card; if you do, draw two cards). An
  optional effect will not be played if it does not have a key in the targets
  dictionary.

  Note that in the case of something like Twofold Askara, it is important to
  include targets for the effects that you will be copying, in addition to the
  target of Twofold Askara's effect.

  There is nothing wrong with including extra keys in targets, just ensure that
  these don't conflict with specific effects, e.g., including a key for both
  sides of an OR clause will raise an Exception.

  Once a move has been constructed, it can be played by calling
  move.apply_to_board(board) (alternatively setting should_add_to_moves to False
  if this is the result of another effect; it was easier to code some effects
  as certain moves, but we don't want those included in the list of moves that
  a player played).
"""

from effects import apply_simple_effect
from card_decoder.effects import SimpleEffect
from events import raise_strategy_card_events
from src.strategies.strategy import Strategy

class Move(object):
  def __init__(self, move_type, card_name, targets):
    assert move_type in ["acquire", "defeat", "play", "activate"]
    if move_type == "acquire":
      assert targets == None

    self.move_type = move_type
    self.card_name = card_name
    self.targets = targets

  def __str__(self):
    return "%s %s" % (self.move_type, self.card_name)

  def apply_to_board(self, board, should_add_to_moves=True):
    if should_add_to_moves:
      board.current_player().moves.append(self)
      board.moves_played_this_turn.append(self)

    move_type_to_fn = {
      'play': self.apply_play,
      'acquire': self.apply_acquire,
      'defeat': self.apply_defeat,
      'activate': self.apply_activate,
    }
    move_type_to_fn[self.move_type](board)

  def _activate_effects(self, board, effect):
    # yuck
    if isinstance(effect, SimpleEffect):
      apply_simple_effect(board, effect, self.targets)
    else:  # compound effect
      effects_with_targets = [e for e in effect.effects if e.effect_index in targets]
      if effect.compound_type == "AND":
        assert len(effects_with_targets) == len(effect.effects)
        self._activate_effects(board, [effects_with_targets])
      else:
        assert len(effects_with_targets) == 1
        self._activate_effects(board, [effects_with_targets[0]])

  def _activate_card_effects(self, board):
    card = board.card_dictionary.find_card(self.card_name)
    self._activate_effects(board, card.effect)

  def apply_play(self, board):
    assert self.move_type == "play"

    if board.card_dictionary.find_card(self.card_name).card_type == "Lifebound Hero":
      board.give_honor(board.current_player(),
        board.current_player().honor_for_lifebound_hero)
      board.current_player().honor_for_lifebound_hero = 0

    # play_card raises an exception if the card isn't there
    board.current_player().play_card(self.card_name)
    self._activate_card_effects(board)

  def apply_acquire(self, board):
    assert self.move_type == "acquire"
    assert self.targets is None

    # raises an exception if the card isn't there, or, e.g. there aren't any
    # more Mystics
    card = board.remove_card_from_center(self.card_name)

    # Checks for, e.g., runes toward mechana constructs; will raise an exception
    # if the player can't afford the card.
    board.current_player().pay_for_acquired_card(card)
    board.current_player().acquire(card)

    raise_strategy_card_events(board,   \
      Strategy.me_acquired_card,        \
      Strategy.opponent_acquired_card,  \
      self.card_name)

  def apply_defeat(self, board):
    assert self.move_type == "defeat"

    # raises an exception if the card isn't there, or, e.g., there aren't any
    # more Heavy Infantry
    card = board.remove_card_from_center(self.card_name)
    assert card.cost <= board.current_player().power_remaining, ("Not enough power" +
      " to defeat %s (%d power remaining)" % (self.card_name, self.power_remaining))

    board.current_player().power_remaining -= card.cost

    if card.name != "Cultist":
      board.give_honor(board.current_player(),
        board.current_player().honor_for_defeating_monster)
      board.current_player().honor_for_defeating_monster = 0

    self._activate_card_effects(board)

    raise_strategy_card_events(board,   \
      Strategy.me_defeated_card,        \
      Strategy.opponent_defeated_card,  \
      self.card_name)

  def apply_activate(self, board):
    assert self.move_type == "activate"

    board.current_player().activate_construct(self.card_name)

    self._activate_card_effects(board)

