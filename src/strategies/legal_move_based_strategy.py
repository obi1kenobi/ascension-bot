"""
  Extends Strategy to be based on the legal moves at a given board position.
"""

from operator import itemgetter
from strategy import Strategy
from src.move_gen import generate_moves

def argmax(l):
  index, element = max(enumerate(l), key=itemgetter(1))
  return index

def argmin(l):
  index, element = min(enumerate(l), key=itemgetter(1))
  return index

class LegalMoveBasedStrategy(Strategy):
  def __init__(self, tag, player_index, num_players, card_dictionary):
    super(LegalMoveBasedStrategy, self).__init__(tag, player_index, num_players, card_dictionary)

  def play_turn(self, board, opponents_previous_moves):
    legal_moves = generate_moves(board)

    while len(legal_moves) > 0:
      self.log('Center: ' + ', '.join([card.name for card in board.center]))
      self.log("Legal moves: " + ', '.join(str(m) for m in legal_moves))
      me = board.current_player()
      self.log("Runes: %d; Power: %d; Honor: %d" %
        (me.runes_remaining, me.power_remaining, me.honor))

      move = self._choose_move(board, legal_moves)

      if move is None:
        # No moves desired
        return

      assert move in legal_moves
      self.play_move(board, move)
      legal_moves = generate_moves(board)

  def _moves_of_type(self, legal_moves, move_type):
    return [move for move in legal_moves if move.move_type == move_type]

  def _move_worth_most_honor(self, moves):
    # This method doesn't make sense when not acquiring or defeating
    assert all(move.move_type == "acquire" or move.move_type == "defeat"
      for move in moves)

    honors = [self.card_dictionary.find_card(move.card_name).honor
        if move.card_name != "Cultist" else 0.5  # dissuade us from killing the cultist
      for move in moves]

    return moves[argmax(honors)]

  # Return either an entry in legal moves or None if the turn should end.
  def _choose_move(self, board, legal_moves):
    raise Exception("_choose_move not implemented")

