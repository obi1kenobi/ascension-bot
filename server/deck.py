from random import shuffle
from card_decoder.decoder import CardDecoder, read_card_counts

class Deck(object):
  def __init__(self, cards):
    self.cards = cards
    shuffle(self.cards)

  @classmethod
  def create_center_deck(cls, card_dictionary):
    card_counts = read_card_counts()
    deck = []
    for card in card_dictionary.cards:
      deck.extend([card] * card_counts[card.name])
    return cls(deck)

  def has_cards_left(self):
    return len(self.cards) > 0

  def shuffle_in_cards(self, cards):
    self.cards.extend(cards)
    shuffle(self.cards)

  def get_next_card(self):
    return self.cards.pop()

