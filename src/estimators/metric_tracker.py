from collections import defaultdict
from estimators import AverageEstimator, WeightedAverageEstimator, LimitedHorizonLinearFitEstimator
from src.constants.effect_indexes import *
import itertools

class MetricTracker(object):
  def __init__(self):
    self.metrics = defaultdict(float)
    self.metrics['eff-deck-size'] = 10.0
    self.metrics['eff-hand-size'] = 5.0

    self.metrics['deck-apprentices'] = 8.0
    self.metrics['deck-militia'] = 2.0
    self.metrics['deck-mystics'] = 0.0
    self.metrics['deck-heavies'] = 0.0

    self.metrics['deck-acquired-heroes'] = 0.0
    self.metrics['deck-acquired-constructs'] = 0.0

    self.metrics['deck-mechana-constructs'] = 0.0
    self.metrics['deck-enlightened-constructs'] = 0.0
    self.metrics['deck-void-constructs'] = 0.0
    self.metrics['deck-lifebound-constructs'] = 0.0

    self.metrics['deck-mechana-heroes'] = 0.0
    self.metrics['deck-enlightened-heroes'] = 0.0
    self.metrics['deck-void-heroes'] = 0.0
    self.metrics['deck-lifebound-heroes'] = 0.0

    self.estimators = {
      'turns-remaining': LimitedHorizonLinearFitEstimator(10),
      'real-deck-size': WeightedAverageEstimator(0.8),
      'real-hand-size': AverageEstimator()
    }

  def _update_acquired_card_type_stats(self, card):
    suffix = None
    if card.is_construct():
      self.metrics['deck-acquired-constructs'] += 1
      suffix = '-constructs'
    elif card.is_hero():
      self.metrics['deck-acquired-heroes'] += 1
      suffix = '-heroes'
    else:
      # something that isn't a construct and isn't a hero was bought?!
      print card
      assert False

    faction = card.faction()
    if faction is None:
      # apprentice, militia, mystic, heavy infantry, monster
      if card.is_mystic():
        self.metrics['deck-mystics'] += 1
      elif card.is_heavy():
        self.metrics['deck-heavies'] += 1
      else:
        # something with no faction was bought, and it wasn't a mystic or heavy?!
        print card
        assert False
    else:
      self.metrics['deck-' + faction.lower() + suffix] += 1

  def _update_hand_size(self, card):
    eff_hand_size_increase = 0

    # TODO(predrag): Switch to checking effects rather than hard-coding effects
    if card.name == "The All-Seeing Eye":
      eff_hand_size_increase += 1

    self.metrics['eff-hand-size'] += eff_hand_size_increase

  def _update_deck_size(self, card):
    eff_deck_size_increase = 1

    if card.is_construct():
      # constructs don't increase the effective deck size
      eff_deck_size_increase = 0
    elif card.is_hero():
      if card.effect.contains_effect_index(DRAW_CARDS_EFFECT):
        chain = itertools.chain.from_iterable(card.effect.generate_legal_effect_sets())
        max_draws = max([x.param for x in chain if x.effect_index == DRAW_CARDS_EFFECT])
        eff_deck_size_increase -= max_draws
      # TODO(predrag): Update effective deck size for conditional 'draw card' effect cards
      # e.g. draw if two constructs in play etc.
    else:
      # can't buy non-construct, non-hero cards
      print card
      assert False

    # Construct-level draw-card effects (All Seeing Eye)
    # are hand size effects, not deck size effects
    self.metrics['eff-deck-size'] += eff_deck_size_increase

  def update_acquired_card(self, card):
    self._update_acquired_card_type_stats(card)
    self._update_deck_size(card)
    self._update_hand_size(card)
    self._update_derived_metrics()

  def update_honor_remaining(self, honor_remaining):
    self.metrics['honor-remaining'] = honor_remaining
    self._update_derived_metrics()

  # turn = one player playing once
  # round = all players playing once
  # total honor handed out with all players playing once
  def update_honor_gained_this_round(self, honor_gained):
    self.metrics['estimate-next-round-honor-gained'] = \
      self.estimators['turns-remaining'].push(honor_gained)
    self._update_derived_metrics()

  # should be called whenever one of the metrics used in a derivation is updated
  def _update_derived_metrics(self):
    self.metrics['eff-deck-cycle-length'] = \
      self.metrics['eff-deck-size'] / self.metrics['eff-hand-size']
    self.metrics['turns-remaining'] = \
      self.estimators['turns-remaining'].estimate_turns_to_sum( \
        self.metrics['honor-remaining'])
