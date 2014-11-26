"""
  Effect represents the effects that happen when cards are played or defeated.
  These come from input/effects.txt.
"""

def _flatten(L):
  return [x for sublist in L for x in sublist]


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

  def contains_effect_index(self, effect_index):
    return self.effect_index == effect_index

  def generate_legal_effect_sets(self):
    sets = [[self]]
    if self.is_optional:
      sets.append([])
    return sets

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

  def contains_effect_index(self, effect_index):
    return any(effect.contains_effect_index(effect_index) for effect in self.effects)

  def generate_legal_effect_sets(self):
    sets = (self._generate_and_legal_effect_sets() if self.compound_type == "AND"
      else self._generate_or_legal_effect_sets())

    if self.is_optional:
      sets.append([])

    return sets

  def _generate_or_legal_effect_sets(self):
    assert self.compound_type == "OR"

    return _flatten([effect.generate_legal_effect_sets() for effect in self.effects])

  def _generate_and_legal_effect_sets(self):
    assert self.compound_type == "AND"

    # choices is now a list of list of lists. The outer level is one for each
    # effect that it has. The next level is the list of legal sets for that
    # specific child.
    choices = [effect.generate_legal_effect_sets() for effect in self.effects]

    return self._generate_cartesian_product(choices)

  # We want to find the cartesian product of the elements in choices.
  # current_set is going to be a list of lists for easy clean up between
  # depths.
  def _generate_cartesian_product(self, choices):
    legal_sets = []

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

