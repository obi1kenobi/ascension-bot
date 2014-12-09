"""
  Definitions of the card classes. Acquirable (constructs and heros) and Monster
  both extend Card. These come from input/acquirable.csv and input/defeatable.csv
  respectively.
"""

from effects import SimpleEffect, CompoundEffect


class CardDictionary(object):
  def __init__(self, cards):
    self.cards = cards

  def find_card(self, card_name):
    cards = [card for card in self.cards if card.name == card_name]
    assert len(cards) == 1, 'Expected to find one "%s", found %d' % (card_name, len(cards))
    return cards[0]


# This shouldn't ever be instantiated directly. Use Acquirable and Defeatable.
class Card(object):
  _valid_card_types = [
    'Hero',  # e.g., Apprentice
    'Enlightened Hero',
    'Enlightened Construct',
    'Void Hero',
    'Void Construct',
    'Mechana Hero',
    'Mechana Construct',
    'Lifebound Hero',
    'Lifebound Construct',
    'Monster'
  ]

  _hero_types = {
    'Hero',  # e.g., Apprentice
    'Enlightened Hero',
    'Void Hero',
    'Mechana Hero',
    'Lifebound Hero'
  }

  _construct_types = {
    'Enlightened Construct',
    'Void Construct',
    'Mechana Construct',
    'Lifebound Construct'
  }

  _monster_types = {
    'Monster'
  }

  _enlightened_types = {
    'Enlightened Hero',
    'Enlightened Construct'
  }

  _void_types = {
    'Void Hero',
    'Void Construct'
  }

  _mechana_types = {
    'Mechana Hero',
    'Mechana Construct'
  }

  _lifebound_types = {
    'Lifebound Hero',
    'Lifebound Construct'
  }

  # card_type is, e.g., "Enlightened Hero", "Lifebound Construct", or "Monster"
  # effect is either a SingleEffect or a CompoundEffect
  def __init__(self, name, cost_str, card_type, effect):
    assert card_type in Card._valid_card_types, "\"%s\" not a valid card type" % card_type
    assert isinstance(effect, SimpleEffect) or isinstance(effect, CompoundEffect), "Damon fucked up"

    self.name = name
    self.cost_str = cost_str
    self.cost = int(cost_str[:-1])
    self.card_type = card_type
    self.effect = effect

  def is_hero(self):
    return self.card_type in Card._hero_types

  def is_construct(self):
    return self.card_type in Card._construct_types

  def is_monster(self):
    return self.card_type in Card._monster_types

  def is_enlightened(self):
    return self.card_type in Card._enlightened_types

  def is_void(self):
    return self.card_type in Card._void_types

  def is_mechana(self):
    return self.card_type in Card._mechana_types

  def is_lifebound(self):
    return self.card_type in Card._lifebound_types

  def is_mystic(self):
    return self.name == "Mystic"

  def is_heavy(self):
    return self.name == "Heavy Infantry"

  def is_apprentice(self):
    return self.name == "Apprentice"

  def is_militia(self):
    return self.name == "Militia"

  def faction(self):
    if self.is_lifebound():
      return 'Lifebound'
    elif self.is_enlightened():
      return 'Enlightened'
    elif self.is_mechana():
      return 'Mechana'
    elif self.is_void():
      return 'Void'
    else:
      # apprentice, militia, mystic, heavy infantry, monster
      return None

  # Returns whether it's possible for a given effect to come from this card.
  def can_use_effect(self, effect_index):
    return self.effect.contains_effect_index(effect_index)

  def get_effect_param(self, effect_index):
    return self.effect.get_effect_param(effect_index)

  # Returns a list of effect lists. Each effect list represents one legal choice
  # of effects.
  def generate_legal_effect_sets(self):
    return self.effect.generate_legal_effect_sets()

  def __eq__(self, other):
    if not isinstance(other, Card):
      return NotImplemented

    return (self.name == other.name and
      self.cost == other.cost and
      self.card_type == other.card_type and
      self.effect == other.effect)

  def __ne__(self, other):
    res = self == other
    if res is NotImplemented:
      return res
    return not res

  # When calling __str__(card), we return this and then a series of lines,
  # one per effect.
  def _title_str(self):
    return ', '.join((self.name, self._cost_str(), self.card_type))

  def _cost_str(self):
    cost_type = ' runes' if self.cost_str[1] == 'R' else ' power'
    return 'Cost: ' + str(self.cost_str[0]) + cost_type

  def __str__(self):
    title_str = self._title_str()
    return '%s\n\t%s' % (title_str, str(self.effect))


# Constructs and Heros. These params are in the order that they appear
# in the csv file.
class Acquirable(Card):
  def __init__(self, name, cost, honor, card_type, effect):
    super(Acquirable, self).__init__(name, cost, card_type, effect)
    assert isinstance(honor, int)
    self.honor = honor

  def __eq__(self, other):
    return (super(Acquirable, self).__eq__(other) and
      isinstance(other, Acquirable) and
      self.honor == other.honor)

  def _title_str(self):
    return ', '.join((self.name, self._cost_str(), str(self.honor) + ' honor', self.card_type))


# This is just a wrapper class around Card to make things a little cleaner
# The params are in the order that they appear in the csv file
class Defeatable(Card):
  def __init__(self, name, cost, card_type, effect):
    super(Defeatable, self).__init__(name, cost, card_type, effect)

    # Either the effect should be a simple effect (gain honor) or it should be
    # an and, where one of the top level effects is gaining honor
    GAIN_HONOR_EFFECT = 4
    if isinstance(effect, SimpleEffect):
      assert effect.effect_index == GAIN_HONOR_EFFECT
      self.honor = effect.param
    else:
      gain_honor_effects = [e for e in effect.effects
        if isinstance(e, SimpleEffect) and e.effect_index == GAIN_HONOR_EFFECT]
      assert len(gain_honor_effects) == 1
      self.honor = gain_honor_effects[0].param

