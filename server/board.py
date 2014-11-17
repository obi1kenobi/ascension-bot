from deck import Deck
from card_decoder.decoder import CardDecoder

NUM_MYSTICS = 30
NUM_HEAVY = 29

# Number of apprentices and militia in each player's starting deck
NUM_APPRENTICE = 8
NUM_MILITIA = 2

HAND_SIZE = 5
CENTER_SIZE = 6


def find_card(cards, card_name):
  cards = [card for card in cards if card.name == card_name]
  assert len(cards) == 1, 'Expected to find one "%s", found %d' % (card_name, len(cards))
  return cards[0]


class Move(object):
  def __init__(self, turn_index, move_type, card_name):
    assert move_type in ["acquire", "defeat", "play"]
    self.turn_index = turn_index
    self.move_type = move_type
    self.card_name = card_name


class PlayerState(object):
  def __init__(self, cards):
    self.discard = []
    self.constructs = []
    self.moves = []
    self.honor = 0

    apprentice = find_card(cards, "Apprentice")
    militia = find_card(cards, "Militia")
    self.deck = Deck([apprentice] * NUM_APPRENTICE + [militia] * NUM_MILITIA)
    self.hand = [self.deck.get_next_card() for i in xrange(HAND_SIZE)]


class Board(object):
  def __init__(self, player_ids):
    self.void = []
    self.mystics = NUM_MYSTICS
    self.heavy = NUM_HEAVY
    self.cultist = 1

    self.cards = CardDecoder().decode_cards()
    self.deck = Deck.create_center_deck(self.cards)
    self.center = [self.deck.get_next_card() for i in xrange(CENTER_SIZE)]

    self.players = {
      player_id: PlayerState(self.cards) for player_id in player_ids
    }
    self.turns = 0
    self.current_turn_index = 0

