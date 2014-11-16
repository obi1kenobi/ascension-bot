from random import shuffle
from card_decoder.decoder import CardDecoder, read_card_counts

class Deck(object):
  def __init__(self, cards):
    self.cards = cards
    shuffle(self.cards)

  @classmethod
  def create_center_deck(cls, cards):
    card_counts = read_card_counts()
    deck = []
    for card in cards:
      deck.extend([card] * card_counts[card.name])
    return cls(deck)

  def get_next_card(self):
    return self.cards.pop()

