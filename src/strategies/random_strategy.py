"""
  Strategy that tests move generation.

  On any given turn:
    while there are moves left to be played
      randomly play a move
"""

from strategy import Strategy
from src.move_gen import generate_moves
import random

TAG = "random"

class RandomStrategy(Strategy):
  def __init__(self, player_index, num_players, card_dictionary):
    super(RandomStrategy, self).__init__(TAG, player_index, num_players, card_dictionary)

  def play_turn(self, board, opponents_previous_moves):
    self.log('Center: ' + ', '.join([card.name for card in board.center]))
    legal_moves = generate_moves(board)

    while len(legal_moves) > 0:
      self.log('Center: ' + ', '.join([card.name for card in board.center]))
      self.log("Legal moves: %s" % '; '.join(str(m) for m in legal_moves))

      move = random.choice(legal_moves)

      self.play_move(board, move)

      legal_moves = generate_moves(board)

  def choose_construct_for_discard(self, board):
    return board.players[self.player_index].constructs[0].name

