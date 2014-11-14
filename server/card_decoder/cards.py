"""
  Definitions of the card classes. Acquirable (constructs and heros) and Monster
  both extend Card. These come from input/acquirable.csv and input/defeatable.csv
  respectively.

  Effect represents the effects that happen when cards are played or defeated.
  These come from input/effects.txt.
"""

class SimpleEffect(object):
  """
    effect_index: Which index in the file this effect refers to.
      Note that because we refer to indices, the effects file
      shouldn't be modified. The reason we use indices is so that
      the AIs and game server have a way to refer to the goodness
      values and functions respectively.
    effect_str: The actual line of text that effect_index refers to.
    param: Optional param. This should be None if the effect doesn't
      require a param.
  """
  # param can be None
  def __init__(self, effect_index, effect_str, param, is_optional):
    SimpleEffect._check_effect_param(effect_str, param)

    self.effect_index = effect_index
    self.effect_str = effect_str
    self.param = param
    self.is_optional = is_optional

  @classmethod
  def _check_effect_param(cls, effect_str, param):
    if '%d' in effect_str:
      assert param is not None, (
        "Param expected for %s, but was passed None" % effect_str)
    else:
      assert param is None, (
        "Param not expected for %s, but was passed one (%s)" % (effect_str, param))

  def __eq__(self, other):
    if not isinstance(other, SimpleEffect):
      return NotImplemented

    if self.effect_index == other.effect_index:
      assert self.effect_str == other.effect_str, (
        """Somehow two effects have the same index but different strings. 
effect_index: %d. 
self.effect_str: %s.
other.effect_str: %s.""" % (self.effect_index, self.effect_str, other.effect_str))

    return (self.effect_index == other.effect_index and
      self.param == other.param and
      self.is_optional == other.is_optional)

  def __ne__(self, other):
    res = self == other
    if res is NotImplemented:
      return res
    return not res

  def __str__(self):
    optional_str = "OPTIONAL: " if self.is_optional else ""

    effect_str = self.effect_str
    if '%d' in effect_str:
      effect_str = effect_str % self.param

    return optional_str + effect_str


# Represents a series of effects combined with AND or OR
class CompoundEffect(object):
  def __init__(self, compound_type, effects, is_optional):
    assert compound_type == 'AND' or compound_type == 'OR', (
      "compound type %s not valid (should be AND or OR)" % compound_type)
    assert len(effects) >= 2
    self.compound_type = compound_type
    self.effects = effects
    self.is_optional = is_optional

  def __eq__(self, other):
    if not isinstance(other, CompoundEffect):
      return NotImplemented

    return (self.compound_type == other.compound_type and
      self.effects == other.effects and
      self.is_optional == other.is_optional)

  def __ne__(self, other):
    res = self == other
    if res is NotImplemented:
      return res
    return not res

  def __str__(self):
    optional_str = 'OPTIONAL: ' if self.is_optional else ''
    effects_str = '; '.join(str(effect) for effect in self.effects)
    return optional_str + self.compound_type + '(%s)' % effects_str


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

  # card_type is, e.g., "Enlightened Hero", "Lifebound Construct", or "Monster"
  def __init__(self, name, cost, card_type, effects):
    assert card_type in Card._valid_card_types, "\"%s\" not a valid card type" % card_type

    self.name = name
    self.cost = cost
    self.card_type = card_type
    self.effects = effects

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
    cost_type = ' runes' if self.cost[1] == 'R' else ' power'
    return self.cost[0] + cost_type

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

