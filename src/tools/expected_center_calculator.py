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
#   expected runes to buy:         14.143
#   expected honor from runes:     8.486
#     expected honor / rune:       0.600
#
#   expected power to defeat:      10.029
#   expected honor from power:     7.029
#     expected honor / power:      0.701
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
  print "  expected runes to buy:         %.03f" % expected_runes_to_buy
  print "  expected honor from runes:     %.03f" % expected_honor_from_runes
  print "    expected honor / rune:       %.03f" % expected_honor_per_rune
  print ""
  print "  expected power to defeat:      %.03f" % expected_power_to_defeat
  print "  expected honor from power:     %.03f" % expected_honor_from_power
  print "    expected honor / power:      %.03f" % expected_honor_per_power
  print ""


def calculate_expected_draws(center_cards):
  total_draw_cards_effect = 34.0
  total_draw_cards = 26.0
  total_cards = len(center_cards)

  normalize_to_cycle_length = 2.5
  cards_per_hand = 5.0
  effect_per_unit = (normalize_to_cycle_length * cards_per_hand + 1) / \
                    (normalize_to_cycle_length * cards_per_hand)

  expected_draw_card_per_bought_card = (total_draw_cards_effect / total_draw_cards) / total_cards

  expected_effect_per_bought_card = expected_draw_card_per_bought_card * effect_per_unit

  print "**************************************************"
  print "Expected draw-card effects:"
  print ""
  print "  expected draw-card effect:     %.03f" % expected_draw_card_per_bought_card
  print "  effect per unit draw-card:     %.03f" % effect_per_unit
  print "  expected effect per card:      %.03f" % expected_effect_per_bought_card
  print ""


def main():
  cards = []
  acquirables = get_acquirables()
  monsters = get_monsters()
  cards.extend(acquirables)
  cards.extend(monsters)

  calculate_expected_center(cards)
  calculate_expected_draws(cards)

if __name__ == "__main__":
  main()
