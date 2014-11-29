#!/usr/bin/python

import random
import time
import logging
import src.game as game
from src import game, log
from src.card_decoder.decoder import CardDecoder
from src.strategies.basic_strategy import BasicStrategy
from src.strategies.toy.basic_estimating_strategy import BasicEstimatingStrategy

# Let the number of strategies be N. This will run N^2 * GAMES_PER_PAIR games.
GAMES_PER_PAIR = 4

STRATEGY_TYPES = [
  BasicStrategy,
  BasicStrategy,
  BasicEstimatingStrategy,
  BasicEstimatingStrategy
]

NUM_PLAYERS = 2

# Returns a dictionary where key is (i, j) meaning staregy i is first player
# and strategy j is second player (note i can equal j). The value is a tuple
# (p1 wins, p2 wins, ties)
def generate_win_count_matrix(seed = None):
  if seed is None:
    seed = int(time.time())

  card_dictionary = CardDecoder().decode_cards()
  win_counts = {}

  for i in xrange(len(STRATEGY_TYPES)):
    for j in xrange(len(STRATEGY_TYPES)):
      a = STRATEGY_TYPES[i]
      b = STRATEGY_TYPES[j]

      # play GAMES_PER_PAIR games, record win counts
      p1_wins = 0
      p2_wins = 0
      ties = 0

      for k in xrange(GAMES_PER_PAIR):
        seed += 1
        random.seed(seed)

        p0 = a(0, NUM_PLAYERS, card_dictionary)
        p1 = b(1, NUM_PLAYERS, card_dictionary)
        print "Using seed %d for %s (player 0) vs %s (player 1)" % (seed, p0.tag, p1.tag)
        victor = game.play_game([p0, p1])
        if victor == "tie":
          ties += 1
        elif victor == "0":
          p1_wins += 1
        elif victor == "1":
          p2_wins += 1
        else:
          raise Exception("Illegal victor: %s" % victor)

      win_counts[(i, j)] = (p1_wins, p2_wins, ties)

  return win_counts

if __name__ == "__main__":
  log.initialize_logging(logging.ERROR)  # don't show log messages

  win_counts = generate_win_count_matrix()

  COLUMN_WIDTH = 20

  # If a (p1 win, p2 win, tie) tuple has three two-digit numbers, it takes 11
  # characters to print. Add two spaces to either side and there is a total of
  # 15 columns to use.
  def pad_tuple(T):
    return str(T).center(COLUMN_WIDTH, ' ')

  print
  print "*" * 50
  print
  print "Tuples are in the form of (p0 wins, p1 wins, ties)"
  print

  card_dictionary = CardDecoder().decode_cards()

  # Print column headings
  print (COLUMN_WIDTH + 3) * ' ',
  for strat in STRATEGY_TYPES:
    # instantiate to get tag, lol...
    tag = strat(0, 1, card_dictionary).tag
    print tag.center(COLUMN_WIDTH - 1, ' '),
  print

  for i in xrange(len(STRATEGY_TYPES)):
    # Print row heading
    tag = STRATEGY_TYPES[i](0, 1, card_dictionary).tag
    print tag.rjust(COLUMN_WIDTH, ' '), '| ',

    # Print row
    print ''.join(str(win_counts[i, j]).center(COLUMN_WIDTH, ' ')
      for j in xrange(len(STRATEGY_TYPES)))

