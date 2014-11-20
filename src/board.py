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

    # self.victor will be None if the game hasn't completely ended yet. (Note
    # this is not the same as the game_over flag; game_over means the honor
    # pool has run out.) Once the game has completely ended (all players have
    # gotten a chance to play during the last round), call compute_victor(),
    # which sets victor to either the string of a player index or "tie"
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

  def compute_victor(self):
    max_honor = max(player.honor for player in self.players)
    player_indices_with_max_honor = [
      i for i in xrange(len(self.players))
        if self.players[i].honor == max_honor
    ]

    if len(player_indices_with_max_honor) > 1:
      self.victor = "tie"
    else:
      assert len(player_indices_with_max_honor) == 1
      self.victor = str(player_indices_with_max_honor[0])

  # This will mark that the game has ended if there is no more honor but it
  # won't compute the victor since some players may still need to play.
  def give_honor(self, player, honor):
    player.honor += honor  # we're allowed to go over the honor_remaining
    self.honor_remaining = max(0, self.honor_remaining - honor)

    if self.honor_remaining == 0:
      self.game_over = True

