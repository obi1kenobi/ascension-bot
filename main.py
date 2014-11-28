#!/usr/bin/python

import logging
from src import game, log
from src.strategies.basic_strategy import BasicStrategy
from src.strategies.user_strategy.user_strategy import UserStrategy
from src.strategies.toy.basic_estimating_strategy import BasicEstimatingStrategy

VERBOSE = True

NUM_PLAYERS = 2

def main():
  log_level = logging.INFO if VERBOSE else logging.ERROR
  log.initialize_logging(log_level)

  strategies = [
    BasicStrategy(0),  # player index 0
    BasicStrategy(1)   # player index 1

    # BasicEstimatingStrategy(0, NUM_PLAYERS),
    # BasicEstimatingStrategy(1, NUM_PLAYERS)

    # UserStrategy(0),
    # UserStrategy(1)
  ]

  victor = game.play_game(strategies)
  if victor == "tie":
    print "Players tied"
  else:
    print "Player %s won" % victor

if __name__ == "__main__":
  main()
