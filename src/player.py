from random import shuffle
from deck import Deck
from copy import copy
from events import raise_strategy_card_events, raise_strategy_deck_events
from card_decoder.cards import Acquirable
from src.strategies.strategy import Strategy

# Number of apprentices and militia in each player's starting deck
NUM_APPRENTICE = 8
NUM_MILITIA = 2

HAND_SIZE = 5


def create_initial_player_deck(card_dictionary):
  apprentice = card_dictionary.find_card("Apprentice")
  militia = card_dictionary.find_card("Militia")
  return Deck([apprentice] * NUM_APPRENTICE + [militia] * NUM_MILITIA)

class Player(object):
  def __init__(self, board, strategy, player_index, card_dictionary):
    self.board = board
    self.player_index = player_index
    self.strategy = strategy
    self.runes_remaining = 0
    self.power_remaining = 0
    self.honor = 0

    self.played_cards = []
    self.acquired_cards = []
    self.discard = []
    self.constructs = []

    self.moves = []

    self.clear_per_turn_state()

    self.deck = create_initial_player_deck(card_dictionary)
    self.hand = []
    for i in xrange(HAND_SIZE):
      self.draw_card()

  def clear_per_turn_state(self):
    # keys in this dictionary should only be at most the number of that card
    # (keys are card names)
    self.num_times_construct_activated = {}
    self.runes_toward_constructs = 0
    self.runes_toward_mechana_constructs = 0
    self.honor_for_lifebound_hero = 0
    self.should_take_additional_turn = False
    self.honor_for_defeating_monster = 0
    self.has_played_mechana_construct = False

  def compute_honor(self):
    all_cards = (self.deck.cards + self.played_cards + self.acquired_cards +
      self.discard + self.constructs)
    assert all(isinstance(card, Acquirable) for card in all_cards)
    return self.honor + sum(card.honor for card in all_cards)

  # This is important to do because this will be used by the player when trying
  # to decide what cards to play. We need to copy it because playing cards
  # involves removing them from the hand, and we don't want to get in a weird
  # state where we're modifying the hand while iterating on it.
  def get_hand(self):
    return copy(self.hand)

  # This attmepts to draw a card from the deck (putting it into the hand).
  # If there are no cards in the deck:
  #   If there are cards in the discard pile, it shuffles those into the deck
  #   Otherwise, it does nothing
  def draw_card(self):
    if not self.deck.has_cards_left():
      if len(self.discard) == 0:
        return

      raise_strategy_deck_events(self.board, 'deck_finished')

      self.deck.shuffle_in_cards(self.discard)
      self.discard = []

    self.hand.append(self.deck.get_next_card())

  # Raises an exception if the card wasn't found. Returns the card
  # that it removed.
  def _remove_card_from_pile(self, pile_name, pile, card_name):
    cards = [card for card in pile if card.name == card_name]
    if len(cards) == 0:
      pile_str = ', '.join(card.name for card in pile)
      raise Exception('Card %s not found in %s (%s)' % (
        card_name, pile_name, hand_str))

    pile.remove(cards[0])
    return cards[0]

  def remove_card_from_hand(self, card_name):
    return self._remove_card_from_pile("hand", self.hand, card_name)

  def remove_card_from_discard(self, card_name):
    return self._remove_card_from_pile("discard", self.discard, card_name)

  def remove_card_from_constructs(self, card_name):
    return self._remove_card_from_pile("constructs", self.constructs, card_name)

  def remove_card_from_played_cards(self, card_name):
    return self._remove_card_from_pile("played cards", self.played_cards, card_name)

  def remove_card_from_acquired_cards(self, card_name):
    return self._remove_card_from_pile("acquired cards", self.acquired_cards, card_name)

  def acquire(self, card):
    # Similar to why we don't play cards into the discard (see below)
    self.acquired_cards.append(card)

  # Raises an exception if there aren't enough runes and credits to pay for it
  def pay_for_acquired_card(self, card):
    cost = card.cost

    if self.considers_card_mechana_construct(card):
      paying = min(self.runes_toward_mechana_constructs, cost)
      self.runes_toward_mechana_constructs -= paying
      cost -= paying

    if card.is_construct():
      paying = min(self.runes_toward_constructs, cost)
      self.runes_toward_constructs -= paying
      cost -= paying

    self.runes_remaining -= cost
    assert self.runes_remaining >= 0, "Did not have enough runes to acquire %s" % (
      card.name)

  # Note that the cards don't go immediately into the discard. This would
  # allow certain strategies that cycle through the deck several times
  # in a turn. Instead, we hold the cards until the end of the turn, at
  # which point we add them to the discard pile.
  def play_card(self, card_name):
    card = self.remove_card_from_hand(card_name)
    if card.is_construct():
      self.constructs.append(card)

      if self.considers_card_mechana_construct(card):
        self.has_played_mechana_construct = True

      raise_strategy_card_events(self.board, 'construct_placed', card_name)

    else:
      self.played_cards.append(card)

  # Doesn't actually perform the effect. Just ensures the player can activate
  def activate_construct(self, card_name):
    count_of_construct = sum(1 for card in self.constructs
      if card.name == card_name)

    assert count_of_construct > 0, ("Player doesn't have %s in play, but tried" +
      " to activate it" % card_name)

    assert self.num_times_construct_activated[card_name] < count_of_construct, ("Player" +
      " has already activated %s as many times as he can (%d)" % (
        card_name, count_of_construct))

  # Move a given card to the discard pile. Raises an exception if the card
  # wasn't found.
  def discard_card(self, card_name):
    card = self.remove_card_from_hand(card_name)
    self.discard.append(card)

  def has_hedron_in_play(self):
    return any(construct.name == "Hedron Link Device" for construct in self.constructs)

  def considers_card_mechana_construct(self, card):
    return card.card_type == "Mechana Construct" or (
      card.card_type == "Construct" and self.has_hedron_in_play())

  # Discard all leftover cards and draw HAND_SIZE new cards (shuffling if need be).
  # Also reset runes and power to 0.
  def end_turn(self):
    self.runes_remaining = 0
    self.power_remaining = 0

    self.discard.extend(self.hand)
    self.discard.extend(self.played_cards)
    self.discard.extend(self.acquired_cards)
    self.hand = []
    self.played_cards = []

    self.clear_per_turn_state()

    for i in xrange(HAND_SIZE):
      self.draw_card()

