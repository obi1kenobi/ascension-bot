from card_decoder.decoder import CardDecoder
from deck import Deck
from player import Player


HONOR_PER_PLAYER = 30

NUM_MYSTICS = 30
NUM_HEAVY = 29

CENTER_SIZE = 6

class Board(object):
  def __init__(self, num_players):
    self.game_over = False
    self.victor = None

    self.void = []
    self.mystics = NUM_MYSTICS
    self.heavy = NUM_HEAVY
    self.cultist = 1

    self.card_dictionary = CardDecoder().decode_cards()

    self.deck = Deck.create_center_deck(self.card_dictionary)
    self.center = [self.deck.get_next_card() for i in xrange(CENTER_SIZE)]

    self.players = [
      Player(self.card_dictionary) for i in xrange(num_players)
    ]
    self.turns = 0
    self.current_player_index = 0
    self.honor_remaining = HONOR_PER_PLAYER * num_players

  def current_player(self):
    return self.players[self.current_player_index]

  def end_turn(self):
    self.current_player().end_turn()
    self.current_player_index = (self.current_player_index + 1) % len(self.players)
    self.turns += 1

    if self.honor_remaining == 0 and self.current_player_index == 0:
      max_honor = max(player.honor for player in self.players)
      player_indices_with_max_honor = [
        i for i in xrange(len(self.players))
          if self.players[i].honor == max_honor
      ]

      if len(player_indices_with_max_honor) > 1:
        self.victor = "tie"
      else:
        assert len(player_indices_with_max_honor) == 1
        self.victor = player_indices_with_max_honor[0]

      self.game_over = True

  def give_honor(self, player, honor):
    player.honor += honor  # we're allowed to go over the honor_remaining
    self.honor_remaining = max(0, self.honor_remaining - honor)

