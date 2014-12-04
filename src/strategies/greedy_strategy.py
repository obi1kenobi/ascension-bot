"""
  Greedy strategy. Plays all its cards then kills the monsters worth the most
  honor and buys the cards worth the most honor at the end of the game.
"""

from legal_move_based_strategy import LegalMoveBasedStrategy

TAG = "greedy"

class GreedyStrategy(LegalMoveBasedStrategy):
  def __init__(self, player_index, num_players, card_dictionary):
    super(GreedyStrategy, self).__init__(TAG, player_index, num_players, card_dictionary)

  def _choose_move(self, board, legal_moves):
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

