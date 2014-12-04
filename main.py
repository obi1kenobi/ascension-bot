#!/usr/bin/python

import logging
from src import game, log
from src.card_decoder.decoder import CardDecoder
from src.strategies.basic_strategy import BasicStrategy
from src.strategies.user_strategy.user_strategy import UserStrategy
from src.strategies.toy.basic_estimating_strategy import BasicEstimatingStrategy
from src.strategies.random_strategy import RandomStrategy
from src.strategies.greedy_strategy import GreedyStrategy

VERBOSE = True

NUM_PLAYERS = 2

def main():
  log_level = logging.INFO if VERBOSE else logging.ERROR
  log.initialize_logging(log_level)

  card_dictionary = CardDecoder().decode_cards()

  strategies = [
    # BasicStrategy(0, NUM_PLAYERS, card_dictionary),  # player index 0
    # BasicStrategy(1, NUM_PLAYERS, card_dictionary)   # player index 1

    # BasicEstimatingStrategy(0, NUM_PLAYERS, card_dictionary),
    # BasicEstimatingStrategy(1, NUM_PLAYERS, card_dictionary)

     # UserStrategy(0, NUM_PLAYERS, card_dictionary),
     # UserStrategy(1, NUM_PLAYERS, card_dictionary)

      # RandomStrategy(0, NUM_PLAYERS, card_dictionary),
      # RandomStrategy(1, NUM_PLAYERS, card_dictionary),

      GreedyStrategy(0, NUM_PLAYERS, card_dictionary),
      GreedyStrategy(1, NUM_PLAYERS, card_dictionary),
  ]

  victor = game.play_game(strategies).victor
  if victor == "tie":
    print "Players tied"
  else:
    print "Player %s won" % victor

if __name__ == "__main__":
  main()
