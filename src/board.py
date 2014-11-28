from card_decoder.decoder import CardDecoder
from deck import Deck
from player import Player


HONOR_PER_PLAYER = 30

NUM_MYSTICS = 30
NUM_HEAVY = 29

CENTER_SIZE = 6

class Board(object):
  def __init__(self, num_players, strategies):
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
      Player(self, self.card_dictionary) for i in xrange(num_players)
    ]
    self.moves_played_this_turn = []
    self.strategies = strategies
    self.turns = 0
    self.current_player_index = 0
    self.honor_remaining = HONOR_PER_PLAYER * num_players

  # Returns the card that it removed. Raises an exception if the card isn't there
  def remove_card_from_center(self, card_name):
    # First check for mystic, heavy, or cultist
    if card_name == "Cultist":
      return self.card_dictionary.find_card(card_name)
    elif card_name == "Mystic":
      self.mystics -= 1
      return self.card_dictionary.find_card(card_name)
    elif card_name == "Heavy Infantry":
      self.heavy -= 1
      return self.card_dictionary.find_card(card_name)

    cards = [card for card in self.center if card.name == card_name]

    if len(cards) == 0:
      center_str = ', '.join(card.name for card in self.center)
      raise Exception("Tried to remove %s from center (%s)" % (
        card_name, center_str))

    self.center.remove(cards[0])

    # TODO(ddoucet): if this is 0, we should shuffle in the void (except not apprentices)
    # TODO(ddoucet): go check where banishing happens and throw out the apprentices
    # and militia and mystics and heavies
    assert len(self.deck.cards) > 0
    self.center.append(self.deck.get_next_card())
    return cards[0]

  def current_player(self):
    return self.players[self.current_player_index]

  def other_players(self):
    return [self.players[i] for i in xrange(len(self.players)) if i != self.current_player_index]

  def end_turn(self):
    self.current_player().end_turn()

    if not self.current_player().should_take_additional_turn:
      self.current_player_index = (self.current_player_index + 1) % len(self.players)
    else:
      self.current_player().should_take_additional_turn = False

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

    # TODO(ddoucet): this doesn't take into account the honor that players have in their decks

  # This will mark that the game has ended if there is no more honor but it
  # won't compute the victor since some players may still need to play.
  def give_honor(self, player, honor):
    player.honor += honor  # we're allowed to go over the honor_remaining
    self.honor_remaining = max(0, self.honor_remaining - honor)

    if self.honor_remaining == 0:
      self.game_over = True

