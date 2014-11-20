#!/usr/bin/python

from src.strategies.basic_strategy import BasicStrategy
from src.board import Board

NUM_PLAYERS = 2

STRATEGIES = [
  BasicStrategy(0),  # player index 0
  BasicStrategy(1)   # player index 1
]

if __name__ == "__main__":
  assert len(STRATEGIES) == NUM_PLAYERS

  board = Board(NUM_PLAYERS)

  while not board.game_over:
    # Give each strategy a chance to make a move before checking for game over
    # again.
    for strategy in STRATEGIES:
      strategy.play_turn(board)
      board.end_turn()

  board.compute_victor()

  for strategy in STRATEGIES:
    strategy.log_end_game(board.victor)

