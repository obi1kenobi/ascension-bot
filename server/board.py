from card_decoder.decoder import CardDecoder
from deck import Deck
from player import Player


HONOR_PER_PLAYER = 30

NUM_MYSTICS = 30
NUM_HEAVY = 29

CENTER_SIZE = 6

class Board(object):
  def __init__(self, player_ids):
    self.game_over = False
    self.victor = None

    self.void = []
    self.mystics = NUM_MYSTICS
    self.heavy = NUM_HEAVY
    self.cultist = 1

    self.card_dictionary = CardDecoder().decode_cards()

    self.deck = Deck.create_center_deck(self.card_dictionary)
    self.center = [self.deck.get_next_card() for i in xrange(CENTER_SIZE)]

    self.player_ids = player_ids
    self.players = {
      player_id: Player(self.card_dictionary) for player_id in player_ids
    }
    self.turns = 0
    self.current_player_index = 0
    self.honor_remaining = HONOR_PER_PLAYER * len(player_ids)

  def current_player(self):
    return self.players[self.player_ids[self.current_player_index]]

  def end_turn(self):
    self.current_player().end_turn()
    self.current_player_index = (self.current_player_index + 1) % len(self.player_ids)
    self.turns += 1

  def give_honor(self, player, honor):
    player.honor += honor  # we're allowed to go over the honor_remaining
    self.honor_remaining = max(0, self.honor_remaining - honor)

    # TODO(ddoucet): what about finishing the round?
    self.game_over = self.honor_remaining == 0

