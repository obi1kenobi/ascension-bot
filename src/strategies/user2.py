"""
  User strategy that gives a list of moves and asks which one to play.
"""

from operator import itemgetter
from strategy import Strategy
from src.move_gen import generate_moves

TAG = "user"

class UserStrategy(Strategy):
  def __init__(self, player_index, num_players, card_dictionary):
    super(UserStrategy, self).__init__(TAG, player_index, num_players, card_dictionary)

  def play_turn(self, board, opponents_previous_moves):
    print "Opponent's Moves:"
    print "\n".join([str(move) for move in opponents_previous_moves])
    print

    legal_moves = self._sorted_moves(generate_moves(board))

    while len(legal_moves) > 0:
      move = self._request_move(board, legal_moves)

      self.play_move(board, move)
      legal_moves = self._sorted_moves(generate_moves(board))

    print "Turn over"
    print

  def _sorted_moves(self, moves):
    move_type_order = ["play", "activate", "acquire", "defeat"]
    return sorted(moves,
      lambda a,b:
        cmp(move_type_order.index(a.move_type),
            move_type_order.index(b.move_type)))

  # max_value is exclusive
  def _request_index(self, prompt, max_value):
    def is_legal_move(s):
      return s.isdigit() and int(s) >= 0 and int(s) < max_value

    num_str = ""
    while not is_legal_move(num_str):
      num_str = raw_input(prompt)

    return int(num_str)

  def _request_move(self, board, legal_moves):
    def format_center_card(card):
      # TODO(ddoucet): display effect strings, cost
      return card.name

    def format_user_card(card):
      # TODO(ddoucet): display effect strings
      return card.name

    def format_move(move):
      # TODO(ddoucet): format effect strings with target
      return str(move)

    # Print the board, the user's constructs, and the user's hand
    # Then wait for input and ask for the user's move (of the list of moves)
    print "Center:"
    print "\n".join([format_center_card(card) for card in board.center])
    print
    if len(board.current_player().constructs) > 0:
      print "Constructs:"
      print "\n".join([format_user_card(card) for card in board.current_player().constructs])
      print
    print "Hand:"
    print "\n".join([format_user_card(card) for card in board.current_player().hand])

    print "Runes:", board.current_player().runes_remaining
    print "Power:", board.current_player().power_remaining
    raw_input("Press enter to see list of moves...")

    print "Moves:"
    print "\n".join([("[%d] " % i) + format_move(move) for i, move in enumerate(legal_moves)])

    return legal_moves[
      self._request_index("Which move would you like to play? ", len(legal_moves))]

  def choose_construct_for_discard(self, board):
    constructs = board.players[self.player_index].constructs
    return constructs[
      self._request_index("Choose a construct to discard ", len(constructs))]

