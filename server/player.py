from random import shuffle
from deck import Deck


# Number of apprentices and militia in each player's starting deck
NUM_APPRENTICE = 8
NUM_MILITIA = 2

HAND_SIZE = 5


def create_initial_player_deck(card_dictionary):
  apprentice = card_dictionary.find_card("Apprentice")
  militia = card_dictionary.find_card("Militia")
  return Deck([apprentice] * NUM_APPRENTICE + [militia] * NUM_MILITIA)

class Player(object):
  def __init__(self, card_dictionary):
    self.runes_remaining = 0
    self.power_remaining = 0
    self.honor = 0

    self.played_cards = []
    self.discard = []
    self.constructs = []

    self.deck = create_initial_player_deck(card_dictionary)
    self.hand = []
    for i in xrange(HAND_SIZE):
      self.draw_card()

  # This attmepts to draw a card from the deck (putting it into the hand).
  # If there are no cards in the deck:
  #   If there are cards in the discard pile, it shuffles those into the deck
  #   Otherwise, it does nothing
  def draw_card(self):
    if not self.deck.has_cards_left():
      if len(self.discard) == 0:
        return

      self.deck.shuffle_in_cards(self.discard)
      self.discard = []

    self.hand.append(self.deck.get_next_card())

  # Raises an exception if the card wasn't found. Returns the card
  # that it removed.
  def _remove_card_from_hand(self, card_name):
    cards = [card for card in self.hand if card.name == card_name]
    if len(cards) == 0:
      hand_str = ', '.join(card.name for card in self.hand)
      raise Exception('Card %s not found in hand (%s)' % (card_name, hand_str))

    self.hand.remove(cards[0])
    return cards[0]

  def acquire(self, card):
    # Similar to why we don't play cards into the discard (see below)
    self.played_cards.append(card)

  # Note that the cards don't go immediately into the discard. This would
  # allow certain strategies that cycle through the deck several times
  # in a turn. Instead, we hold the cards until the end of the turn, at
  # which point we add them to the discard pile.
  def play_card(self, card_name):
    card = self._remove_card_from_hand(card_name)
    self.played_cards.append(card)

  # Move a given card to the discard pile. Raises an exception if the card
  # wasn't found.
  def discard_card(self, card_name):
    card = self._remove_card_from_hand(card_name)
    self.discard.append(card)

  # Discard all leftover cards and draw HAND_SIZE new cards (shuffling if need be).
  # Also reset runes and power to 0.
  def end_turn(self):
    self.runes_remaining = 0
    self.power_remaining = 0

    self.discard.extend(self.hand)
    self.discard.extend(self.played_cards)
    self.hand = []
    self.played_cards = []

    for i in xrange(HAND_SIZE):
      self.draw_card()

