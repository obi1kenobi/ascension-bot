"""
  Strategy that tests move generation.

  On any given turn:
    while there are moves left to be played
      randomly play a move
"""

import random
from legal_move_based_strategy import LegalMoveBasedStrategy

TAG = "random"

class RandomStrategy(LegalMoveBasedStrategy):
  def __init__(self, player_index, num_players, card_dictionary):
    super(RandomStrategy, self).__init__(TAG, player_index, num_players, card_dictionary)

  def _choose_move(self, board, legal_moves):
    return random.choice(legal_moves)

  def choose_construct_for_discard(self, board):
    return board.players[self.player_index].constructs[0].name

