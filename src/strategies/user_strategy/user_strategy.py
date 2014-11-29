"""
"""

from ..strategy import Strategy
from src.moves import Move
from os import sys
from copy import copy

TAG = "user"

GAIN_RUNES_EFFECT = 3
GAIN_HONOR_EFFECT = 4
GAIN_POWER_EFFECT = 5

def get_string_of_cards(hand):
  return str([(("[%d] " % idx) + (hand[idx].name)) for idx in xrange(len(hand))])

def print_game_state(player, board):
    print "\n"
    print "Hand: " + get_string_of_cards(player.get_hand())
    print "Constructs: " + get_string_of_cards(player.constructs)
    print "Runes = %d    Power = %d\n" % (player.runes_remaining, player.power_remaining)

    print "Center: " + get_string_of_cards(board.center)
    print "\t\t\t" + str(["[6] Cultist", "[7] Mystic(%d left)" % board.mystics, "[8] Heavy Infantry(%d left)" % board.heavy])
    print ""

def read_symbol():
    return sys.stdin.readline()[0]

def read_string():
    s = sys.stdin.readline()
    return s[:len(s) - 1]

class UserStrategy(Strategy):
  def __init__(self, player_index, num_players, card_dictionary):
    super(UserStrategy, self).__init__(TAG, player_index, num_players, card_dictionary)

  def play_card(self, cards_not_played):
    targets = {GAIN_RUNES_EFFECT: [], GAIN_HONOR_EFFECT: [], GAIN_POWER_EFFECT: []}

    # The user wants to play a card, give him the list of cards that are not played or say that he has played all
    if len(cards_not_played) == 0:
      print "All cards have been played"
    else:
      print "Which card? " + str(cards_not_played) + (" or [a]All" if len(cards_not_played) > 1 else "")
      card_idx = read_symbol() 
      cards_to_play = []

      if card_idx == 'a':
        cards_to_play = copy(cards_not_played)
      else:
        if not card_idx.isdigit() or int(card_idx) not in cards_not_played:
          print "Not a valid input"
        else:
          cards_to_play = [int(card_idx)]
      
      for idx in cards_to_play:
        self.play_move(self.board, Move("play", self.hand[idx].name, targets))
        cards_not_played.remove(idx)

  def acquire_card(self, cards_not_acquired):
    if len(cards_not_acquired) == 0:
      print "No cards to acquire"
    else:
      print "Which card? " + str(cards_not_acquired) 
      card_idx = read_symbol() 

      if not card_idx.isdigit() or int(card_idx) not in cards_not_acquired:
        print "Not a valid input"
      else:
        card_idx = int(card_idx)
        if card_idx == 7:
          card = self.board.card_dictionary.find_card("Mystic")
        elif card_idx == 8:
          card = self.board.card_dictionary.find_card("Heavy Infantry")
        else: 
          card = self.board.center[card_idx]
          
        cost = card.cost
        if self.player.considers_card_mechana_construct(card):
          paying = min(self.player.runes_toward_mechana_constructs, cost)
          cost -= paying

        if "Construct" in card.card_type:
          paying = min(self.player.runes_toward_constructs, cost)
          cost -= paying

        if cost > self.player.runes_remaining:
          print "Don't have enough runes to acquire %s" % card.name
        else:
          self.play_move(self.board, Move("acquire", card.name, None))

  def defeat_card(self, cards_not_defeated):
    if len(cards_not_defeated) == 0:
      print "No cards to defeat"
    else:
      print "Which card? " + str(cards_not_defeated) 
      card_idx = read_symbol() 

      if not card_idx.isdigit() or int(card_idx) not in cards_not_defeated:
        print "Not a valid input"
      else:
        card_idx = int(card_idx)
        if card_idx == 6:
          card = self.board.card_dictionary.find_card("Cultist")
        else: 
          card = self.board.center[card_idx]

        if card.cost > self.player.power_remaining:
          print "Don't have enough power to defeat %s" % card.name
        else:
          targets = []

           # print "Please give %d effect targets: " % card.effect.param
           # for _ in xrange(card.effect.param):
            #  targets.append(read_string())
              # TODO(Rumen): That's super unsafe and will definitely assert, because 
              # we will give a wrong target. A way to fix it is have two modes for all of the 
              # functions into board, one which returns false and one which asserts, so 
              # we can have play_move just return false and say that the move was invalid
              # Another way to do it is to copy one more time all of the effects functions
              # and check if the targets are valid

          self.play_move(self.board, Move("defeat", card.name, {GAIN_HONOR_EFFECT: targets}))

  def activate_card(self, constructs):
    targets = {GAIN_RUNES_EFFECT: [], GAIN_HONOR_EFFECT: [], GAIN_POWER_EFFECT: []}
    if len(constructs) == 0:
      print "No constructs"
    else:
      print "Which card? " + str(constructs) 
      card_idx = read_symbol() 

      if not card_idx.isdigit() or int(card_idx) not in constructs:
        print "Not a valid input"
      else:
        card_idx = int(card_idx)
        card_name = self.player.constructs[card_idx].name

        count_of_construct = sum(1 for card in self.player.constructs
              if card.name == card_name)

        if count_of_construct > 0:
          print ("Player doesn't have %s in play, but tried" +
                     " to activate it" % card_name)
        elif self.player.num_times_construct_activated[card_name] < count_of_construct:
              ("Player has already activated %s as many times as he can (%d)" % (
                    card_name, count_of_construct))
        else:
          self.play_move(self.board, Move("activate", card.name, targets))

  def play_turn(self, board, opponents_previous_moves):
    assert board.current_player() == board.players[self.player_index]

    self.board = board
    player = board.current_player()
    self.player = player

    hand = player.get_hand()
    self.hand = hand 
    targets = {GAIN_RUNES_EFFECT: [], GAIN_HONOR_EFFECT: [], GAIN_POWER_EFFECT: []}

    cards_not_played = [idx for idx in xrange(len(hand))]

    while True:
      print_game_state(player, board)
      print "Do you want to [0]play, [1]acquire, [2]defeat, [3]activate card or [4]end turn?"
      inp = read_symbol()

      if inp == '0':
        self.play_card(cards_not_played)
        
      if inp == '1':
        cards_not_acquired = [idx for idx in xrange(len(hand)) if hand[idx].card_type != "Monster"]
        if board.mystics > 0:
          cards_not_acquired.append(7)
        if board.heavy > 0:
          cards_not_acquired.append(8)

        self.acquire_card(cards_not_acquired)

      if inp == '2':
        cards_not_defeated = [idx for idx in xrange(len(hand)) if hand[idx].card_type == "Monster"]
        cards_not_defeated.append(6)
        self.defeat_card(cards_not_defeated)

      if inp == '3':
        constructs = [idx for idx in xrange(len(player.constructs))]
        self.activate_card(constructs)

      if inp == '4':
        break

    self.log("Honor: %d" % player.honor)

  def choose_construct_for_discard(self, board):
    while True:
      print "Which construct do you want to discard? " + get_string_of_cards(self.player.constructs)
      card_idx = read_symbol() 

      if not card_idx.isdigit() or int(card_idx) not in constructs:
        print "Not a valid input"
      else: 
        return self.player.constructs[card_idx].card_name

