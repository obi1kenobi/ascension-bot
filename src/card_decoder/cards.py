"""
  Definitions of the card classes. Acquirable (constructs and heros) and Monster
  both extend Card. These come from input/acquirable.csv and input/defeatable.csv
  respectively.
"""

def _flatten(L):
  return [x for sublist in L for x in sublist]

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
  def __init__(self, name, cost_str, card_type, effects):
    assert card_type in Card._valid_card_types, "\"%s\" not a valid card type" % card_type

    self.name = name
    self.cost_str = cost_str
    self.cost = int(cost_str[:-1])
    self.card_type = card_type
    self.effects = effects

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
    return any(effect.contains_effect_index(effect_index)
      for effect in self.effects)

  # Returns a list of effect lists. Each effect list represents one legal choice
  # of effects.
  def generate_legal_effect_sets(self):
    # choices is now a list of list of lists. The outer level is one for each
    # effect that it has. The next level is the list of legal sets for that
    # specific child.
    choices = [effect.generate_legal_effect_sets() for effect in self.effects]

    legal_sets = []

    # We want to find the cartesian product of the elements in choices.
    # current_set is going to be a list of lists for easy clean up between
    # depths.
    def find_cartesian_product(current_set, index):
      if index == len(choices):
        legal_sets.append(_flatten(current_set))
        return

      # Try each possibility in choices[index]. Note that choices[index] is a
      # 2d list. The outer level is all legal sets for that effect, and the
      # inner level is a list of effects (e.g., the AND clause)
      for choice in choices[index]:
        current_set.append(choice)
        find_cartesian_product(current_set, index + 1)
        current_set.pop()

    find_cartesian_product([], 0)

    return legal_sets

  def __eq__(self, other):
    if not isinstance(other, Card):
      return NotImplemented

    return (self.name == other.name and
      self.cost == other.cost and
      self.card_type == other.card_type and
      self.effects == other.effects)

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
    return str(self.cost_str) + cost_type

  def __str__(self):
    effect_str = '\n\t' + '\n\t'.join(str(effect) for effect in self.effects)

    title_str = self._title_str()
    return title_str + effect_str


# Constructs and Heros. These params are in the order that they appear
# in the csv file.
class Acquirable(Card):
  def __init__(self, name, cost, honor, card_type, effects):
    super(Acquirable, self).__init__(name, cost, card_type, effects)
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
  def __init__(self, name, cost, card_type, effects):
    super(Defeatable, self).__init__(name, cost, card_type, effects)

