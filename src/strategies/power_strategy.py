"""
  Strategy that just buys Heavies and then defeats the strongest monster over
  and over again.

  TODO(ddoucet): this could be changed a bit to buy better cards (e.g. some
  with more power).
"""

from legal_move_based_strategy import LegalMoveBasedStrategy

TAG = "power"

def argmax(l):
  index, element = max(enumerate(l), key=itemgetter(1))
  return index

class PowerStrategy(LegalMoveBasedStrategy):
  def __init__(self, player_index, num_players, card_dictionary):
    super(PowerStrategy, self).__init__(TAG, player_index, num_players, card_dictionary)

  def _choose_move(self, board, legal_moves):
    activates = self._moves_of_type(legal_moves, "activate")
    if len(activates) > 0:  # This should only happen after defeating xeron
      return activates[0]

    # Check if there are any cards that we can play
    plays = self._moves_of_type(legal_moves, "play")
    if len(plays) > 0:
      return plays[0]

    # Buy any heavy infantry
    buy_heavy_moves = [move for move in legal_moves
      if move.move_type == "acquire" and move.card_name == "Heavy Infantry"]

    if len(buy_heavy_moves) > 0:
      return buy_heavy_moves[0]

    # TODO(ddoucet): technically this is greedy about picking and doesn't use DP
    # Choose defeats that give us the most honor
    defeats = self._moves_of_type(legal_moves, "defeat")
    if len(defeats) > 0:
      return self._move_worth_most_honor(defeats)

    return None  # No moves we want to play

  def choose_construct_for_discard(self, board):
    # We should only have constructs after defeating xeron. We don't really care.
    return board.players[self.player_index].constructs[0].name

