import files
from decoder import get_dict, read_card_counts
from cards import Card, Acquirable, Defeatable
from effects import SimpleEffect, CompoundEffect

# Effects are referenced by index, so it's very important that the
# data file not be reordered. This tests that the effects are in
# the order that we expect them to be.
def test_effects_not_reodered():
  EXPECTED_EFFECTS = [
    "Discard %d cards",
    "Draw %d cards",
    "Gain %d runes",
    "Gain %d honor",
    "Gain %d power",
    "Banish %d card in hand",
    "Banish %d card in center",
    "Banish %d card from discard pile",
    "Defeat monster of %d power or less without cost",
    "Pay %d less runes when acquiring a mechana construct this turn",
    "Acquire a hero with cost %d or less without cost. Place it on top of your deck",
    "First time you play a lifebound hero, gain %d honor",
    "Draw %d card when putting a Mechana Construct into play",
    "Banish this card to take an additional turn",
    "Pay %d less runes when acquiring a construct this turn",
    "First time you defeat a monster, gain %d honor",
    "Draw a card if you control 2 or more constructs",
    "Gain %d honor for each faction among Constructs you control",
    "Each opponent must destroy a construct",
    "Once per turn, when you acquire another Mechana Construct, put it directly into play",
    "Treat all constructs as mechana constructs",
    "Take a card at random from each opponent's hand and add that to your hand",
    "If you have played another lifebound hero, gain %d power",
    "Each opponent destroys all but one construct",
    "Gain %d power for each Mechana Construct in play that you control",
    "Copy the effect of a Hero",
    "Unbanishable. Acquire or defeat any card in the center without paying its cost."
  ]

  effects = files.read_lines('input/effects.txt')
  fail_message = """It looks like effects.txt has been changed.
If it was just a minor change (rewording a description), just change it in this test.
Be careful about reordering effects, though, because we reference effects by indices
so you'll probably break a lot of things."""

  assert effects == EXPECTED_EFFECTS, fail_message


def fetch_simple_effect(effects, effect_index, param, is_optional):
  return SimpleEffect(effect_index, effects[effect_index], param, is_optional)

def compound(effect_list):
  return effect_list[0] if len(effect_list) == 1 else CompoundEffect('AND', effect_list, False)


# Picks a few cards and tests that their values are what we expect.
# Also tests that we have the correct number of cards.
def test_various_cards():
  effects = [''] + files.read_lines('input/effects.txt')
  NUM_CARDS = 53
  SELECTED_CARDS = [
    # Simple tests
    Acquirable("Apprentice", "0R", 0, "Hero", compound([
      fetch_simple_effect(effects, 3, 1, False)
    ])),
    Acquirable("Hedron Link Device", "7R", 7, "Mechana Construct", compound([
      fetch_simple_effect(effects, 21, None, False)
    ])),

    # Test multiple effects
    Acquirable("Arbiter of the Precipice", "4R", 1, "Void Hero", compound([
      fetch_simple_effect(effects, 2, 2, False),
      fetch_simple_effect(effects, 6, 1, False)
    ])),

    # Test optional effects
    Acquirable("Seer of the Forked Path", "2R", 1, "Enlightened Hero", compound([
      fetch_simple_effect(effects, 2, 1, False),
      fetch_simple_effect(effects, 7, 1, True)
    ])),

    # Test compound effects (and construct)
    Acquirable("Yggdrasil Staff", "4R", 2, "Lifebound Construct", compound([
      fetch_simple_effect(effects, 5, 1, False),
      CompoundEffect("AND", [
        fetch_simple_effect(effects, 3, -4, False),
        fetch_simple_effect(effects, 4, 3, False)
      ], True)
    ])),

    # Test defeatable (and with comma in name)
    Defeatable("Xeron, Duke of Lies", "6P", "Monster", compound([
      fetch_simple_effect(effects, 4, 3, False),
      fetch_simple_effect(effects, 22, None, False)
    ]))
  ]

  card_dictionary = get_dict()
  assert len(card_dictionary.cards) == NUM_CARDS

  for card in SELECTED_CARDS:
    check_card_correct(card_dictionary, card)


# Looks up expected_card by name in cards, checks that there is exactly
# one matching card with that name, and then checks that the two cards
# are equal.
def check_card_correct(card_dictionary, expected_card):
  actual_card = card_dictionary.find_card(expected_card.name)
  assert actual_card == expected_card, (
    "Expected: %s\nActual: %s" % (str(expected_card), str(cards_with_name[0])))


# Asserts that the total number of cards in the initial deck is 100
def test_correct_number_of_cards():
  NUM_CARDS = 100

  counts = read_card_counts()
  actual = sum(counts[card] for card in counts.keys())
  assert actual == NUM_CARDS, "Expected %d cards, got %d" % (NUM_CARDS, actual)

