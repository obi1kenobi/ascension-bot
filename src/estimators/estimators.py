import numpy as np

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

  def push(self, value):
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
