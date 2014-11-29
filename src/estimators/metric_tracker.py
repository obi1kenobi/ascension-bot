from collections import defaultdict
from estimators import AverageEstimator, WeightedAverageEstimator, LimitedHorizonLinearFitEstimator
from src.constants.effect_indexes import *
import itertools

def updatesDerived(f):
  def wrapper(self, *args, **kwargs):
    f(self, *args, **kwargs)
    self._update_derived_metrics()
  return wrapper


class MetricTracker(object):
  def __init__(self, initial_honor_remaining):
    self.metrics = defaultdict(float)
    self.metrics['honor-in-cards'] = 0.0   # currently not tracked
    self.metrics['honor-in-tokens'] = 0.0
    self.metrics['honor-total'] = 0.0
    self.metrics['honor-remaining'] = float(initial_honor_remaining)  # remaining in tokens

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

  @updatesDerived
  def update_acquired_card(self, card):
    self._update_owned_card_type_stats(card, acquired=True)
    self._update_deck_size(card, acquired=True)
    self._update_hand_size(card, acquired=True)

  @updatesDerived
  def update_banished_card_from_deck(self, card):
    self._update_owned_card_type_stats(card, acquired=False)
    self._update_deck_size(card, acquired=False)
    self._update_hand_size(card, acquired=False)

  @updatesDerived
  def update_honor(self, my_honor_tokens, total_honor_tokens_remaining):
    # turn = one player playing once
    # round = all players playing once
    # total honor handed out with all players playing once
    honor_delta = self.metrics['honor-remaining'] - total_honor_tokens_remaining

    # the total honor left on the board cannot increase
    assert honor_delta >= 0

    self.metrics['estimate-next-round-honor-gained'] = \
      self.estimators['turns-remaining'].push(honor_delta)

    self.metrics['honor-in-tokens'] = my_honor_tokens
    self.metrics['honor-remaining'] = total_honor_tokens_remaining


  ### Only private helper methods from this point on ###


  def _update_owned_card_type_stats(self, card, acquired=True):
    suffix = None
    delta = 1 if acquired else -1
    if card.is_construct():
      self.metrics['deck-acquired-constructs'] += delta
      assert self.metrics['deck-acquired-constructs'] >= 0
      suffix = '-constructs'
    elif card.is_hero():
      self.metrics['deck-acquired-heroes'] += delta
      assert self.metrics['deck-acquired-heroes'] >= 0
      suffix = '-heroes'
    else:
      # something that isn't a construct and isn't a hero was bought?!
      print card
      assert False

    faction = card.faction()
    if faction is None:
      # apprentice, militia, mystic, heavy infantry, monster
      if card.is_mystic():
        self.metrics['deck-mystics'] += delta
        assert self.metrics['deck-mystics'] >= 0
      elif card.is_heavy():
        self.metrics['deck-heavies'] += delta
        assert self.metrics['deck-heavies'] >= 0
      else:
        # something with no faction was bought, and it wasn't a mystic or heavy?!
        print card
        assert False
    else:
      key = 'deck-' + faction.lower() + suffix
      self.metrics[key] += delta
      assert self.metrics[key] >= 0

  def _update_hand_size(self, card, acquired=True):
    eff_hand_size_increase = 0
    delta = 1 if acquired else -1

    # TODO(predrag): Switch to checking effects rather than hard-coding effects
    if card.name == "The All-Seeing Eye":
      eff_hand_size_increase += delta

    self.metrics['eff-hand-size'] += eff_hand_size_increase

  def _update_deck_size(self, card, acquired=True):
    delta = 1 if acquired else -1
    eff_deck_size_increase = delta

    if card.is_construct():
      # constructs don't change the effective deck size
      eff_deck_size_increase = 0
    elif card.is_hero():
      if card.effect.contains_effect_index(DRAW_CARDS_EFFECT):
        chain = itertools.chain.from_iterable(card.effect.generate_legal_effect_sets())
        max_draws = max([x.param for x in chain if x.effect_index == DRAW_CARDS_EFFECT])
        eff_deck_size_increase -= max_draws * delta
      # TODO(predrag): Update effective deck size for conditional 'draw card' effect cards
      # e.g. draw if two constructs in play etc.
    else:
      # can't buy non-construct, non-hero cards
      print card
      assert False

    # Construct-level draw-card effects (All Seeing Eye)
    # are hand size effects, not deck size effects
    self.metrics['eff-deck-size'] += eff_deck_size_increase

    # should be called whenever one of the metrics used in a derivation is updated
  def _update_derived_metrics(self):
    self.metrics['honor-total'] = \
      self.metrics['honor-in-cards'] + self.metrics['honor-in-tokens']
    self.metrics['eff-deck-cycle-length'] = \
      self.metrics['eff-deck-size'] / self.metrics['eff-hand-size']
    self.metrics['turns-remaining'] = \
      self.estimators['turns-remaining'].estimate_turns_to_sum( \
        self.metrics['honor-remaining'])
