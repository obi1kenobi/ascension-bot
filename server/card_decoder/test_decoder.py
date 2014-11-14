import files
from decoder import CardDecoder
from cards import SimpleEffect, CompoundEffect, Card, Acquirable, Defeatable

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
    "Pay %d less runes when acquiring a mehchana construct this turn",
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
  fail_message = """It looks like input/effects.txt has been changed.
If it was just a minor change (rewording a description), just change it in this test.
Be careful about reordering effects, though, because we reference effects by indices
so you'll probably break a lot of things."""

  assert effects == EXPECTED_EFFECTS, fail_message


def fetch_simple_effect(effects, effect_index, param, is_optional):
  return SimpleEffect(effect_index, effects[effect_index], param, is_optional)


# Picks a few cards and tests that their values are what we expect.
# Also tests that we have the correct number of cards.
def test_various_cards():
  effects = [''] + files.read_lines('input/effects.txt')
  NUM_CARDS = 53
  SELECTED_CARDS = [
    # Simple tests
    Acquirable("Apprentice", "0R", 0, "Hero", [
      fetch_simple_effect(effects, 3, 1, False)
    ]),
    Acquirable("Hedron Link Device", "7R", 7, "Mechana Construct", [
      fetch_simple_effect(effects, 21, None, False)
    ]),

    # Test multiple effects
    Acquirable("Arbiter of the Precipice", "4R", 1, "Void Hero", [
      fetch_simple_effect(effects, 2, 2, False),
      fetch_simple_effect(effects, 6, 1, False)
    ]),

    # Test optional effects
    Acquirable("Seer of the Forked Path", "2R", 1, "Enlightened Hero", [
      fetch_simple_effect(effects, 2, 1, False),
      fetch_simple_effect(effects, 7, 1, True)
    ]),

    # Test compound effects (and construct)
    Acquirable("Yggdrasil Staff", "4R", 2, "Lifebound Construct", [
      fetch_simple_effect(effects, 5, 1, False),
      CompoundEffect("AND", [
        fetch_simple_effect(effects, 3, -4, False),
        fetch_simple_effect(effects, 4, 3, False)
      ], True)
    ]),

    # Test defeatable (and with comma in name)
    Defeatable("Xeron, Duke of Lies", "6P", "Monster", [
      fetch_simple_effect(effects, 4, 3, False),
      fetch_simple_effect(effects, 22, None, False)
    ])
  ]

  cards = CardDecoder().decode_cards()
  assert len(cards) == NUM_CARDS

  for card in SELECTED_CARDS:
    check_card_correct(cards, card)


# Looks up expected_card by name in cards, checks that there is exactly
# one matching card with that name, and then checks that the two cards
# are equal.
def check_card_correct(cards, expected_card):
  cards_with_name = [card for card in cards if card.name == expected_card.name]
  assert len(cards_with_name) == 1, (
    'Card "%s" has %d associated cards; should have 1' % (
      expected_card.name, len(cards_with_name)))

  assert cards_with_name[0] == expected_card, (
    "Expected: %s\nActual: %s" % (str(expected_card), str(cards_with_name[0])))

