from random import shuffle
from card_decoder.decoder import CardDecoder

class Deck(object):
  def __init__(self, cards):
    self.cards = cards
    shuffle(self.cards)

  @classmethod
  def create_center_deck(cls, cards):
    return cls(cards)
    # TODO(ddoucet): use proper counts of each card

  def get_next_card(self):
    return self.cards.pop()

