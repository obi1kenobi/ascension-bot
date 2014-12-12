
MAX_ROUNDS = 15

TOTAL_HONOR_TOKENS = 60.0

STARTING_RUNES = 4.0
STARTING_POWER = 1.0

# can't have more than 10 runes in one hand (5 mystics)
# not counting draw-card effects
RUNES_CAP = 10.0

# can't have more than 10 power in one hand (5 heavies)
POWER_CAP = 10.0

# realistically, can't really draw more than 5 cards on a regular basis
DRAW_CARDS_CAP = 2.0

def simulate_power_strategy():
  honor_per_rune = 0.5  # buys only heavy infantry

  # other values from calculator
  honor_per_power = 0.700855

  # each heavy adds about 0.429 power per draw in expectation
  # normalizing around the expected contribution of the fifth heavy
  # old deck: 10 power (4 heavy, 2 militia), 14 cards total
  # new deck: 12 power (5 heavy, 2 militia), 15 cards total
  # hand = 5 cards
  power_per_rune = ((12.0 / 15.0) - (10.0 / 14.0)) * 5.0
  assert power_per_rune > 0

  runes = STARTING_RUNES
  power = STARTING_POWER

  total_honor_tokens = 0.0
  total_honor_cards = 0.0
  honor_history = []
  card_honor_history = []
  token_honor_history = []

  for i in xrange(MAX_ROUNDS):
    total_honor_cards += runes * honor_per_rune
    total_honor_tokens += power * honor_per_power

    # all runes used to purchase power
    power += runes * power_per_rune
    power = min(power, POWER_CAP)

    total_honor = total_honor_tokens + total_honor_cards

    card_honor_history.append(total_honor_cards)
    token_honor_history.append(total_honor_tokens)
    honor_history.append(total_honor)

  print "**************************************************"
  print "Power strategy honor history:"
  print "cards: %s" % card_honor_history
  print "tokens: %s" % token_honor_history
  print "total: %s" % honor_history
  print ""

  return (card_honor_history, token_honor_history, honor_history)


# mystic_round_cutoff is the round number when the strategy
# stops buying mystics and starts buying normal cards
def simulate_mechana_strategy(mystic_round_cutoff):
  assert mystic_round_cutoff <= MAX_ROUNDS
  assert mystic_round_cutoff >= 0

  honor_per_rune = 0.600000             # from calculator, when buying mix of cards
  honor_per_power = 0.700855

  runes = STARTING_RUNES
  power = STARTING_POWER

  runes_per_card = 2.357143             # from calculator
  draw_card_effect_per_card = 1.038089  # from calculator

  # each mystic adds about 0.455 runes per draw in expectation
  # normalizing around the expected contribution of the second mystic
  # old deck: 10 runes (1 mystics, 8 apprentice), 11 cards total
  # new deck: 12 runes (2 mystics, 8 apprentice), 12 cards total
  # hand = 5 cards
  # this is higher than the power-per-heavy because fewer mystics are usually bought
  runes_per_mystic = ((12.0/12.0) - (10.0/11.0))*5
  assert runes_per_mystic > 0
  mystic_cost = 3.0
  honor_per_mystic = 1.0

  total_honor_tokens = 0.0
  total_honor_cards = 0.0
  honor_history = []
  card_honor_history = []
  token_honor_history = []
  draw_card_multiplier = 1.0

  for i in xrange(MAX_ROUNDS):
    effective_runes = runes * draw_card_multiplier
    effective_power = power * draw_card_multiplier
    if i < mystic_round_cutoff:
      # buying only mystics
      mystics_bought = effective_runes / mystic_cost
      total_honor_cards += mystics_bought * honor_per_mystic
      total_honor_tokens += effective_power * honor_per_power

      runes += mystics_bought * runes_per_mystic
      runes = min(runes, RUNES_CAP)
    else:
      # buying only center deck cards
      cards_bought = effective_runes / runes_per_card

      total_honor_cards += effective_runes * honor_per_rune
      total_honor_tokens += effective_power * honor_per_power
      draw_card_multiplier *= draw_card_effect_per_card ** cards_bought  # yes, that's an exponent
      draw_card_multiplier = min(draw_card_multiplier, DRAW_CARDS_CAP)

    total_honor = total_honor_tokens + total_honor_cards

    card_honor_history.append(total_honor_cards)
    token_honor_history.append(total_honor_tokens)
    honor_history.append(total_honor)

  print "**************************************************"
  print "Mechana-mystic-%d strategy honor history:" % mystic_round_cutoff
  print "cards: %s" % card_honor_history
  print "tokens: %s" % token_honor_history
  print "total: %s" % honor_history
  print ""

  return (card_honor_history, token_honor_history, honor_history)


def simulate_lifebound_strategy(mystic_round_cutoff):
  assert mystic_round_cutoff <= MAX_ROUNDS
  assert mystic_round_cutoff >= 0

  # total card honor in honor-per-turn cards = 19
  # total rune cost of honor-per-turn cards  = 39
  honor_per_rune = 19.0 / 39.0
  honor_per_power = 0.700855            # from calculator

  runes = STARTING_RUNES
  power = STARTING_POWER

  runes_per_card = 2.357143             # from calculator
  draw_card_effect_per_card = 1.038089  # from calculator

  honor_per_turn_per_card = 0.105714    # from calculator

  # each mystic adds about 0.455 runes per draw in expectation
  # normalizing around the expected contribution of the second mystic
  # old deck: 10 runes (1 mystics, 8 apprentice), 11 cards total
  # new deck: 12 runes (2 mystics, 8 apprentice), 12 cards total
  # hand = 5 cards
  # this is higher than the power-per-heavy because fewer mystics are usually bought
  runes_per_mystic = ((12.0/12.0) - (10.0/11.0))*5
  assert runes_per_mystic > 0
  mystic_cost = 3.0
  honor_per_mystic = 1.0

  total_honor_tokens = 0.0
  total_honor_cards = 0.0
  honor_history = []
  card_honor_history = []
  token_honor_history = []
  draw_card_multiplier = 1.0
  honor_per_turn = 0.0

  for i in xrange(MAX_ROUNDS):
    effective_runes = runes * draw_card_multiplier
    effective_power = power * draw_card_multiplier
    effective_honor_per_turn = honor_per_turn * draw_card_multiplier
    if i < mystic_round_cutoff:
      # buying only mystics
      mystics_bought = effective_runes / mystic_cost
      total_honor_cards += mystics_bought * honor_per_mystic
      total_honor_tokens += effective_power * honor_per_power

      runes += mystics_bought * runes_per_mystic
      runes = min(runes, RUNES_CAP)
    else:
      # buying only center deck cards
      cards_bought = effective_runes / runes_per_card

      total_honor_cards += effective_runes * honor_per_rune
      total_honor_tokens += effective_power * honor_per_power + effective_honor_per_turn

      honor_per_turn += cards_bought * honor_per_turn_per_card
      draw_card_multiplier *= draw_card_effect_per_card ** cards_bought  # yes, that's an exponent
      draw_card_multiplier = min(draw_card_multiplier, DRAW_CARDS_CAP)

    total_honor = total_honor_tokens + total_honor_cards

    card_honor_history.append(total_honor_cards)
    token_honor_history.append(total_honor_tokens)
    honor_history.append(total_honor)

  print "**************************************************"
  print "Lifebound-mystic-%d strategy honor history:" % mystic_round_cutoff
  print "cards: %s" % card_honor_history
  print "tokens: %s" % token_honor_history
  print "total: %s" % honor_history
  print ""

  return (card_honor_history, token_honor_history, honor_history)


def calculate_payoffs(a_strat, b_strat):
  a_card_honor, a_token_honor, a_total_honor = a_strat
  b_card_honor, b_token_honor, b_total_honor = b_strat

  for i in xrange(MAX_ROUNDS):
    total_honor_in_tokens = a_token_honor[i] + b_token_honor[i]
    if total_honor_in_tokens >= TOTAL_HONOR_TOKENS:
      # game over after round i, calculate payoffs
      total_honor = a_total_honor[i] + b_total_honor[i]
      return (a_total_honor[i] / total_honor, b_total_honor[i] / total_honor)

  # no game will realistically ever last more than MAX_ROUNDS
  # but because of the simplifications in the model, mechana vs lifebound
  # may take a very long time
  # print "Stopping game after %d rounds" % MAX_ROUNDS

  total_honor = a_total_honor[-1] + b_total_honor[-1]
  return (a_total_honor[-1] / total_honor, b_total_honor[-1] / total_honor)


def construct_payoff_matrix(first_strats, second_strats):
  return [[calculate_payoffs(a, b) for b in second_strats] for a in first_strats]


# tries to find a deviation that makes either player better off
# compared to their payoffs at payoff_matrix[x][y]
def find_better_off_from(payoff_matrix, x, y):
  p1_payoff, p2_payoff = payoff_matrix[x][y]
  # print "Considering (%d, %d), payoffs %s" % (x, y, str(payoff_matrix[x][y]))
  for i in xrange(len(payoff_matrix)):
    if payoff_matrix[i][y][0] > p1_payoff:
      # print "x = %d improves it for P1 to %s" % (i, str(payoff_matrix[i][y]))
      return True

  for i in xrange(len(payoff_matrix[0])):
    if payoff_matrix[x][i][1] > p2_payoff:
      # print "y = %d improves it for P2 to %s" % (i, str(payoff_matrix[x][i]))
      return True

  # print "Found Nash equilibrium!"
  return False


def find_nash_equilibria(payoff_matrix):
  equilibria = []
  for i in xrange(len(payoff_matrix)):
    for j in xrange(len(payoff_matrix[0])):
      if not find_better_off_from(payoff_matrix, i, j):
        equilibria.append((i, j))
  return equilibria


def main():
  round_cutoff = MAX_ROUNDS
  power_strats = [simulate_power_strategy()]
  mechana_strats = [simulate_mechana_strategy(i) for i in xrange(round_cutoff)]
  lifebound_strats = [simulate_lifebound_strategy(i) for i in xrange(round_cutoff)]

  power_vs_mechana = construct_payoff_matrix(power_strats, mechana_strats)
  power_vs_mechana_equilibria = find_nash_equilibria(power_vs_mechana)

  print "**************************************************"
  print "Power vs Mechana"
  # print "  -> payoff matrix:"
  # print power_vs_mechana
  print "  -> Nash equilibria:"
  print power_vs_mechana_equilibria
  print "  -> Nash payoffs:"
  for eq in power_vs_mechana_equilibria:
    x, y = eq
    print power_vs_mechana[x][y]
  print ""

  power_vs_lifebound = construct_payoff_matrix(power_strats, lifebound_strats)
  power_vs_lifebound_equilibria = find_nash_equilibria(power_vs_lifebound)

  print "**************************************************"
  print "Power vs Lifebound"
  # print "  -> payoff matrix:"
  # print power_vs_lifebound
  print "  -> Nash equilibria:"
  print power_vs_lifebound_equilibria
  print "  -> Nash payoffs:"
  for eq in power_vs_lifebound_equilibria:
    x, y = eq
    print power_vs_lifebound[x][y]
  print ""

  mechana_vs_lifebound = construct_payoff_matrix(mechana_strats, lifebound_strats)
  mechana_vs_lifebound_equilibria = find_nash_equilibria(mechana_vs_lifebound)

  print "**************************************************"
  print "Mechana vs Lifebound"
  # print "  -> payoff matrix:"
  # print mechana_vs_lifebound
  print "  -> Nash equilibria:"
  print mechana_vs_lifebound_equilibria
  print "  -> Nash payoffs:"
  for eq in mechana_vs_lifebound_equilibria:
    x, y = eq
    print mechana_vs_lifebound[x][y]
  print ""


if __name__ == "__main__":
  main()
