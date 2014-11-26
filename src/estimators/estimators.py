import numpy as np
from math import sqrt

# Estimate = average of all pushed values
class AverageEstimator(object):
  def __init__(self):
    self.sum = 0.0
    self.count = 0

  def push(self, value):
    self.sum += value
    self.count += 1
    return self.estimate()

  def estimate(self):
    return self.sum / self.count

# Estimate = (1-coeff) * previous_estimate + coeff * value
class WeightedAverageEstimator(object):
  def __init__(self, coeff):
    self.coeff = coeff
    self.previous = 0.0
    self.called = False

  def push(self, value):
    if not self.called:
        self.previous = value
        self.called = True
    else:
        self.previous = (self.previous * (1-self.coeff)) + (self.coeff * value)

    return self.estimate()

  def estimate(self):
    return self.previous

# Estimate = interpolated next value based on best uniform linear-fit of history
class LinearFitEstimator(object):
  def __init__(self):
    self.history = []
    self.m = 0.0
    self.c = 0.0

  # updates the y = mx + c equation based on a
  # least-squares linear fit of the history
  def _update(self):
    x = np.array([i for i in xrange(len(self.history))])
    A = np.vstack([x, np.ones(len(self.history))]).T
    self.m, self.c = np.linalg.lstsq(A, np.array(self.history))[0]

  def push(self, value):
    self.history.append(value)
    self._update()
    return self.estimate()

  def estimate(self):
    x = len(self.history)
    return (self.m * x) + self.c

  # solves quadratic functions of the form ax^2 + bx + c = 0
  # returns a pair of real solutions (x1, x2), or None if there are none
  @staticmethod
  def _solve_quadratic(a, b, c):
    print "solving (%f)x^2 + (%f)x + (%f) = 0" % (a, b, c)
    if a == 0:
      x = -c/b
      if x < 0:
        return None
      return (x, x)
    else:
      discriminant = b*b - 4*a*c
      if discriminant < 0:
        return None
      discriminant = sqrt(discriminant)

      x1 = (-b + discriminant) / (2*a)
      x2 = (-b - discriminant) / (2*a)

      print "solutions: (%f, %f)" % (x1, x2)

      return (x1, x2)

  def estimate_turns_to_sum(self, s):
    # finds the number of new push/estimate turns it will take to produce a sum equal to s
    # assuming pushed values follow the estimated model.
    if self.m == 0:
      return None

    h = float(len(self.history))
    total = float(s) + h*self.c + h*(h-1)*self.m/2

    # total = sum (mx + c) for x = 0 ... t-1
    # total = m/2 * t * (t-1) + ct
    # total = m/2 * t^2 + (c - m/2) * t

    solns = LinearFitEstimator._solve_quadratic(self.m/2, (self.c - self.m/2), -total)
    if solns is None:
      return None

    (t1, t2) = solns

    # count how many new turns are needed, in addition to the h existing ones
    t1 -= h
    t2 -= h

    if t1 < 0 and t2 < 0:
      return None
    elif t1 >= 0 and t2 >= 0:
      return min(t1, t2)
    elif t1 >= 0:
      return t1
    elif t2 >= 0:
      return t2

class LimitedHorizonLinearFitEstimator(LinearFitEstimator):
  def __init__(self, horizon):
    super(LimitedHorizonLinearFitEstimator, self).__init__()
    self.horizon = horizon
    assert self.horizon > 0

  def push(self, value):
    if len(self.history) >= self.horizon:
      self.history.pop(0)
    super(LimitedHorizonLinearFitEstimator, self).push(value)
