import itertools
from src.card_decoder.decoder import CardDecoder

# itertools.combinations(iterable, count)

def make_card(runes_to_buy, honor_from_runes, power_to_defeat, honor_from_power):
  return (float(runes_to_buy),     \
          float(honor_from_runes), \
          float(power_to_defeat),  \
          float(honor_from_power))

def get_monsters():
  mephits = [(0, 0, 3, 2)] * 3
  tormented_souls = [(0, 0, 3, 1)] * 3
  tricksters = [(0, 0, 3, 1)] * 4

  mistakes = [(0, 0, 4, 4)] * 4
  widows = [(0, 0, 4, 3)] * 4

  sea_tyrants = [(0, 0, 5, 5)] * 3
  wind_tyrants = [(0, 0, 5, 3)] * 3

  earth_tyrants = [(0, 0, 6, 5)] * 2
  xerons = [(0, 0, 6, 3)]

  avatars = [(0, 0, 7, 4)]

  monsters = mephits + \
             tormented_souls + \
             tricksters + \
             mistakes + \
             widows + \
             sea_tyrants + \
             wind_tyrants + \
             earth_tyrants + \
             xerons + \
             avatars

  return monsters

def get_acquirables():
  acquirables = CardDecoder()._decode_acquirables()
  return [make_card(c.cost, c.honor, 0, 0) for c in acquirables]

###
# Output:
# **************************************************
# Expected center:
#
#   expected runes to buy:         14.142857
#   expected honor from runes:     8.485714
#     expected runes / card:       2.357143
#     expected honor / rune:       0.600000
#
#   expected power to defeat:      10.028571
#   expected honor from power:     7.028571
#     expected power / card:       1.671429
#     expected honor / power:      0.700855
#
###
def calculate_expected_center(center_cards):
  total_combinations = 0
  total_runes_to_buy = 0.0
  total_honor_from_runes = 0.0
  total_power_to_defeat = 0.0
  total_honor_from_power = 0.0

  center_size = 6

  for card in center_cards:
    runes_to_buy, honor_from_runes, power_to_defeat, honor_from_power = card
    total_combinations += 1
    total_runes_to_buy += runes_to_buy
    total_honor_from_runes += honor_from_runes
    total_power_to_defeat += power_to_defeat
    total_honor_from_power += honor_from_power

  expected_runes_to_buy = total_runes_to_buy / total_combinations * center_size
  expected_honor_from_runes = total_honor_from_runes / total_combinations * center_size
  expected_power_to_defeat = total_power_to_defeat / total_combinations * center_size
  expected_honor_from_power = total_honor_from_power / total_combinations * center_size

  expected_honor_per_rune = expected_honor_from_runes / expected_runes_to_buy
  expected_honor_per_power = expected_honor_from_power / expected_power_to_defeat

  print "**************************************************"
  print "Expected center:"
  print ""
  print "  expected runes to buy:         %.06f" % expected_runes_to_buy
  print "  expected honor from runes:     %.06f" % expected_honor_from_runes
  print "    expected runes / card:       %.06f" % (expected_runes_to_buy / center_size)
  print "    expected honor / rune:       %.06f" % expected_honor_per_rune
  print ""
  print "  expected power to defeat:      %.06f" % expected_power_to_defeat
  print "  expected honor from power:     %.06f" % expected_honor_from_power
  print "    expected power / card:       %.06f" % (expected_power_to_defeat / center_size)
  print "    expected honor / power:      %.06f" % expected_honor_per_power
  print ""

###
# Output:
# **************************************************
# Expected draw-card effects:
#
#   expected draw-card per card:   0.485714
#   effect per unit draw-card:     1.080000
#     expected effect per card:    1.038089
#
###
def calculate_expected_draws(center_cards):
  total_draw_cards_effect = 34.0
  total_draw_cards = 26.0
  total_cards = float(len(center_cards))

  normalize_to_cycle_length = 2.5
  cards_per_hand = 5.0
  effect_per_unit = (normalize_to_cycle_length * cards_per_hand + 1) / \
                    (normalize_to_cycle_length * cards_per_hand)

  expected_draw_card_per_bought_card = total_draw_cards_effect / total_cards

  expected_effect_per_bought_card = effect_per_unit ** expected_draw_card_per_bought_card

  # effect_per ^ (1/draw_per) = effect_per_unit
  # 1/draw_per * log effect_per = log effect_per_unit
  # log effect_per = log effect_per_unit * draw_per
  # effect_per = effect_per_unit ^ draw_per

  print "**************************************************"
  print "Expected draw-card effects:"
  print ""
  print "  expected draw-card per card:   %.06f" % expected_draw_card_per_bought_card
  print "  effect per unit draw-card:     %.06f" % effect_per_unit
  print "    expected effect per card:    %.06f" % expected_effect_per_bought_card
  print ""

###
# Output:
# **************************************************
# Expected draw-card effects:
#
#   expected honor per card:       0.105714
#
###
def calculate_expected_honor_per_turn(center_cards):
  total_cards = float(len(center_cards))
  cards_per_hand = 5.0

  normalize_to_cycle_length = 2.5

  direct_honor_cards = 7
  direct_honor_per_turn_effect = 9.0
  avatar_golems = 2
  avatar_golem_honor_per_play = 2.0
  yggdrasil_staffs = 2

  # honor per rune = 0.600
  # honor per power for lifebound = 0.500
  # yggdrasil gives 1 power and 3 honor for 4 runes
  # upside = 0.500 + 3 - 4 * 0.600 = 1.1
  yggdrasil_staff_honor_per_turn = 1.1

  total_honor_with_all_cards = direct_honor_per_turn_effect + \
                               (avatar_golem_honor_per_play * avatar_golems) + \
                               (yggdrasil_staffs * yggdrasil_staff_honor_per_turn * \
                                normalize_to_cycle_length)

  total_honor_per_turn_cards = direct_honor_cards + avatar_golems + yggdrasil_staffs

  expected_honor_per_card = total_honor_with_all_cards / total_cards / normalize_to_cycle_length
  # expected_honor_per_hand = total_honor_with_all_cards / total_cards * cards_per_hand

  print "**************************************************"
  print "Expected draw-card effects:"
  print ""
  print "  expected honor per card:       %.06f" % expected_honor_per_card
  #print "  expected honor per turn:       %.06f" % expected_honor_per_hand
  print ""

def main():
  cards = []
  acquirables = get_acquirables()
  monsters = get_monsters()
  cards.extend(acquirables)
  cards.extend(monsters)

  calculate_expected_center(cards)
  calculate_expected_draws(cards)
  calculate_expected_honor_per_turn(cards)

if __name__ == "__main__":
  main()
