#!/usr/bin/python

import random
import time
import logging
import src.game as game
from src import game, log
from src.card_decoder.decoder import CardDecoder
from src.strategies.basic_strategy import BasicStrategy
from src.strategies.toy.basic_estimating_strategy import BasicEstimatingStrategy
from src.strategies.random_strategy import RandomStrategy
from src.strategies.greedy_strategy import GreedyStrategy

# Let the number of strategies be N. This will run N^2 * GAMES_PER_PAIR games.
GAMES_PER_PAIR = 32

STRATEGY_TYPES = [
  BasicStrategy,
  RandomStrategy,
  GreedyStrategy,
]

NUM_PLAYERS = 2

# Plays num_games with p0_type and p1_type. Returns a tuple
# (new_seed, (p0 win %, tie %, p0 total honor fraction when winning, p0 total
# fraction when losing)).
def play_games(card_dictionary, p0_type, p1_type, num_games, seed):
  p0_wins = 0
  ties = 0
  total_hf_winning = 0
  total_hf_losing = 0

  for k in xrange(num_games):
    seed += 1
    random.seed(seed)

    p0 = p0_type(0, NUM_PLAYERS, card_dictionary)
    p1 = p1_type(1, NUM_PLAYERS, card_dictionary)
    print "Using seed %d for %s (player 0) vs %s (player 1)" % (seed, p0.tag, p1.tag)
    board = game.play_game([p0, p1])
    victor = board.victor
    if victor == "tie":
      ties += 1
    elif victor == "0":
      p0_wins += 1
      total_hf_winning += board.honor_fraction(0)
    elif victor == "1":
      total_hf_losing += board.honor_fraction(0)
    else:
      raise Exception("Illegal victor: %s" % victor)

  p0_losses = num_games - p0_wins - ties
  average_hf_winning = 0 if p0_wins == 0 else total_hf_winning / p0_wins
  average_hf_losing = 0 if p0_losses == 0 else total_hf_losing / p0_losses
  average_hf = (total_hf_winning + total_hf_losing + 0.5 * ties) / num_games
  win_frac = float(p0_wins) / num_games
  tie_frac = float(ties) / num_games
  return (seed, (win_frac, tie_frac, average_hf_winning, average_hf_losing, average_hf))

# Returns a dictionary where key is (i, j) meaning strategy i is first player
# and strategy j is second player (note i can equal j). The value is a tuple
# (win %, tie %, average fraction of total honor when winning, average fraction
# when losing, average fraction overall)
def generate_matrix(seed = None):
  if seed is None:
    seed = int(time.time())

  card_dictionary = CardDecoder().decode_cards()
  matrix = {}

  for i in xrange(len(STRATEGY_TYPES)):
    for j in xrange(len(STRATEGY_TYPES)):
      a = STRATEGY_TYPES[i]
      b = STRATEGY_TYPES[j]

      seed, matrix[i, j] = play_games(card_dictionary, a, b, GAMES_PER_PAIR, seed)

  return matrix

if __name__ == "__main__":
  log.initialize_logging(logging.ERROR)  # don't show log messages

  matrix = generate_matrix()

  COLUMN_WIDTH = 35

  # If a (p1 win, p2 win, tie) tuple has three two-digit numbers, it takes 11
  # characters to print. Add two spaces to either side and there is a total of
  # 15 columns to use.
  def pad_tuple(T):
    return str(T).center(COLUMN_WIDTH, ' ')

  print
  print "*" * 50
  print
  print "Rows are player 0, columns are player 1. Data is from the perspective"
  print "of player 0."
  print
  print "Each entry is a tuple of the form"
  print "\t(win %, tie %, average fraction of total honor when winning, average"
  print "\tfraction when losing, average fraction overall"
  print

  card_dictionary = CardDecoder().decode_cards()

  # Print column headings
  print (COLUMN_WIDTH - 5) * ' ',
  print "p0\p1  ",
  for strat in STRATEGY_TYPES:
    # instantiate to get tag, lol...
    tag = strat(0, 1, card_dictionary).tag
    print tag.center(COLUMN_WIDTH - 1, ' '),
  print

  def tuple_str(T):
    def i_to_str(i):
      return str(i) if isinstance(i, int) else "%.3f" % i
    return ("(%s)" % (','.join(i_to_str(i) for i in T))).center(COLUMN_WIDTH, ' ')

  for i in xrange(len(STRATEGY_TYPES)):
    # Print row heading
    tag = STRATEGY_TYPES[i](0, 1, card_dictionary).tag
    print tag.rjust(COLUMN_WIDTH, ' '), '| ',

    # Print row
    print ''.join(tuple_str(matrix[i, j])
      for j in xrange(len(STRATEGY_TYPES)))

