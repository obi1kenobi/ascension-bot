"""
  Greedy strategy. Plays all its cards then kills the monsters worth the most
  honor and buys the cards worth the most honor at the end of the game.
"""

from operator import itemgetter
from strategy import Strategy
from src.move_gen import generate_moves

TAG = "greedy"

def argmax(l):
  index, element = max(enumerate(l), key=itemgetter(1))
  return index

class GreedyStrategy(Strategy):
  def __init__(self, player_index, num_players, card_dictionary):
    super(GreedyStrategy, self).__init__(TAG, player_index, num_players, card_dictionary)

  def play_turn(self, board, opponents_previous_moves):
    legal_moves = generate_moves(board)

    while len(legal_moves) > 0:
      self.log("Legal moves: " + ', '.join(str(m) for m in legal_moves))
      move = self._choose_move(legal_moves)

      self.play_move(board, move)
      legal_moves = generate_moves(board)

  def _moves_of_type(self, legal_moves, move_type):
    return [move for move in legal_moves if move.move_type == move_type]

  def _move_worth_most_honor(self, moves):
    # This method doesn't make sense when not acquiring or defeating
    assert all(move.move_type == "acquire" or move.move_type == "defeat"
      for move in moves)

    honors = [self.card_dictionary.find_card(move.card_name).honor
      for move in moves]

    return moves[argmax(honors)]

  def _choose_move(self, legal_moves):
    # Activate any constructs
    activates = self._moves_of_type(legal_moves, "activate")
    if len(activates) > 0:
      return activates[0]

    # Check if there are any cards that we can play
    # TODO(ddoucet): this could technically banish important cards... Generally,
    # though, we probably won't end up getting banish cards because they aren't
    # worth as much honor
    plays = self._moves_of_type(legal_moves, "play")
    if len(plays) > 0:
      return plays[0]

    # TODO(ddoucet): technically this is greedy about picking and doesn't use DP
    # Choose defeats that give us the most honor
    defeats = self._moves_of_type(legal_moves, "defeat")
    if len(defeats) > 0:
      return self._move_worth_most_honor(defeats)

    # Choose acquires that give us the most honor
    acquires = self._moves_of_type(legal_moves, "acquire")

    assert len(acquires) == len(legal_moves)  # All moves should be one of
    # these types, and we've found that none of the other types have any moves.

    assert len(acquires) > 0  # Shouldn't call this if there are no moves

    # TODO(ddoucet): same as above about greediness (not DP)
    return self._move_worth_most_honor(acquires)

  def choose_construct_for_discard(self, board):
    # Just pick the first one because we're greedy and don't care.
    return board.players[self.player_index].constructs[0].name

