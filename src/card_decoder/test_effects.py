"""
  Test Card.can_use_effect and Card.generate_legal_effect_sets
"""

import pytest

@pytest.fixture(scope="module")
def card_dictionary():
  from decoder import get_dict
  return get_dict()

def assert_correct_effect((expected_index, expected_param), effect):
  assert expected_index == effect.effect_index, "Expected index %d, got %d" % (
    expected_index, effect.effect_index)

  assert expected_param == effect.param, "Expected param %d, got %d" % (
    expected_param, effect.param)

# Check that a card contains all effects in should_contain_list and that the
# list of legal sets that it generates is equal to legal_sets. legal_sets is
# a list of tuple lists. Each tuple list represents a legal effect set, and
# each tuple is (effect_index, param).
# Unfortunately, legal_sets is order-sensitive.
def _test_card(card, should_contain_list, expected_sets):
  for effect_index in should_contain_list:
    assert card.can_use_effect(effect_index), "%s should contain effect index %d" % (
      card.card_name, effect_index)

  actual_sets = card.generate_legal_effect_sets()
  for (expected_set, actual_set) in zip(expected_sets, actual_sets):
    for (expected_effect, actual_effect) in zip(expected_set, actual_set):
      assert_correct_effect(expected_effect, actual_effect)

def test_simple_effect(card_dictionary):
  apprentice = card_dictionary.find_card("Apprentice")

  # effects: 3(1)
  _test_card(apprentice, [3], [[(3, 1)]])

def test_multiple_optionals(card_dictionary):
  mistake = card_dictionary.find_card("Mistake of Creation")

  # effects: 4(4),7(1)?,8(1)?
  _test_card(mistake, [4, 7, 8], [
      [(4, 4)],
      [(4, 4), (7, 1)],
      [(4, 4), (8, 1)],
      [(4, 4), (7, 1), (8, 1)]
  ])

def test_optional_and(card_dictionary):
  yggdrasil = card_dictionary.find_card("Yggdrasil Staff")

  # effects: 5(1),AND(3(-4);4(3))?
  _test_card(yggdrasil, [5, 3, 4], [
    [(5, 1)],
    [(5, 1), (3, -4), (4, 3)]
  ])

def test_optional_or(card_dictionary):
  shade = card_dictionary.find_card("Shade of the Black Watch")

  # effects: 5(2),OR(6(1);8(1))?
  _test_card(shade, [5, 6, 8], [
    [(5, 2), (6, 1)],
    [(5, 2), (8, 1)],
    [(5, 2)],
  ])

def test_no_param(card_dictionary):
  hedron = card_dictionary.find_card("Hedron Link Device")

  # effects: 21()
  _test_card(hedron, [21], [[(21, None)]])

def test_effect_series(card_dictionary):
  arbiter = card_dictionary.find_card("Arbiter of the Precipice")

  # effects: 2(2),6(1)
  _test_card(arbiter, [2, 6], [[(2, 2), (6, 1)]])

