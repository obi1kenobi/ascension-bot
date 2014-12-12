"""
  User strategy that gives a list of moves and asks which one to play.
"""

from operator import itemgetter
from strategy import Strategy
from src.move_gen import generate_moves
import os

TAG = "user"

def clear_screen():
  os.system('cls' if os.name == 'nt' else 'clear')

class UserStrategy(Strategy):
  def __init__(self, player_index, num_players, card_dictionary):
    super(UserStrategy, self).__init__(TAG, player_index, num_players, card_dictionary)

  def play_turn(self, board, opponents_previous_moves):
    clear_screen()
    print "Opponent's Moves:"
    print "\n".join([str(move) for move in opponents_previous_moves])
    raw_input("Press Enter to continue...")

    legal_moves = self._sorted_moves(generate_moves(board))

    while len(legal_moves) > 0:
      move = self._request_move(board, legal_moves)

      if move is None:
        break

      self.play_move(board, move)
      legal_moves = self._sorted_moves(generate_moves(board))

    print "Turn over"
    raw_input("Press Enter to continue...")

  def _sorted_moves(self, moves):
    move_type_order = ["play", "activate", "acquire", "defeat"]
    return sorted(moves,
      lambda a,b:
        cmp((move_type_order.index(a.move_type), a.card_name),
            (move_type_order.index(b.move_type), b.card_name)))

  # max_value is exclusive
  def _request_index(self, prompt, max_value):
    def is_legal_move(s):
      return s.isdigit() and int(s) >= 0 and int(s) < max_value

    num_str = ""
    while not is_legal_move(num_str):
      num_str = raw_input(prompt)

    return int(num_str)

  def _request_move(self, board, legal_moves):
    def get_distinct_moves(moves):
      distinct = []
      def has_move(m):
        return any((m.move_type == move.move_type and \
          m.card_name == move.card_name and \
          m.targets == move.targets) for move in distinct)

      for move in moves:
        if not has_move(move):
          distinct.append(move)

      return distinct

    def print_user_card_group(group_name, cards):
      print group_name + ":"
      print "\n".join([str(card) for card in cards])
      print

    # Print the board, the user's constructs, and the user's hand
    # Then wait for input and ask for the user's move (of the list of moves)
    print "Your Honor:", board.current_player().honor
    print "Other Player's Honor:", board.players[self.player_index ^ 1].honor
    print

    print "Center:"
    print "\n".join([str(card) for card in board.center])
    print

    print_user_card_group("Discard Pile", board.current_player().discard)

    if len(board.current_player().constructs) > 0:
      print_user_card_group("Constructs", board.current_player().constructs)

    print_user_card_group("Played Cards", board.current_player().played_cards)

    print "Hand:"
    print "\n".join([str(card) for card in board.current_player().hand])

    print "Runes:", board.current_player().runes_remaining
    print "Power:", board.current_player().power_remaining
    raw_input("Press Enter to see list of moves...")

    print "Moves:"
    distinct_moves = get_distinct_moves(legal_moves)
    print "\n".join([("[%d] " % i) + str(move) for i, move in enumerate(distinct_moves)])
    print "[%d] End turn" % len(distinct_moves)

    move_index = self._request_index("Which move would you like to play? ",
      len(distinct_moves) + 1)
    return distinct_moves[move_index] if move_index < len(distinct_moves) else None

  def choose_construct_for_discard(self, board):
    constructs = board.players[self.player_index].constructs
    return constructs[
      self._request_index("Choose a construct to discard ", len(constructs))]

