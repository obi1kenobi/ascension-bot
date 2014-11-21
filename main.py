#!/usr/bin/python

import logging
from src.strategies.basic_strategy import BasicStrategy
from src.board import Board
from src import log

NUM_PLAYERS = 2

def play_game(strategies):
  assert len(strategies) == NUM_PLAYERS

  board = Board(NUM_PLAYERS)

  while not board.game_over:
    # Give each strategy a chance to make a move before checking for game over
    # again.
    for strategy in strategies:
      strategy.play_turn(board)
      board.end_turn()

  board.compute_victor()

  for strategy in strategies:
    strategy.log_end_game(board.victor)

  return board.victor

if __name__ == "__main__":
  strategies = [
    BasicStrategy(0),  # player index 0
    BasicStrategy(1)   # player index 1
  ]

  log.initialize_logging(logging.INFO)

  victor = play_game(strategies)
  if victor == "tie":
    print "Players tied"
  else:
    print "Player %s won" % victor

