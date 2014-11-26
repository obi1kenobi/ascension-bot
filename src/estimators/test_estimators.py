import random
from estimators import AverageEstimator, WeightedAverageEstimator, LinearFitEstimator, LimitedHorizonLinearFitEstimator

def test_average_estimator():
  est = AverageEstimator()
  rand_number = random.randint(-100, 100)

  for i in xrange(100):
    est.push(rand_number)

  assert abs(est.estimate() - rand_number) < 1e-9

def test_weighted_estimator():
  est = WeightedAverageEstimator(random.random())
  rand_number = random.randint(-100, 100)

  for i in xrange(100):
    est.push(rand_number)

  assert abs(est.estimate() - rand_number) < 1e-9


  est = WeightedAverageEstimator(0.2)
  est.push(5)
  est.push(10)

  assert abs(est.estimate() - 6) < 1e-9

def linear_fit_estimator_test1(est):
  rand_number = random.randint(-100, 100)

  for i in xrange(100):
    est.push(rand_number)

  assert abs(est.estimate() - rand_number) < 1e-9

def linear_fit_estimator_test2(est):
  est.push(100)
  est.push(200)
  assert abs(est.estimate() - 300) < 1e-9
  assert abs(est.estimate_turns_to_sum(300) - 1) < 1e-9
  assert abs(est.estimate_turns_to_sum(700) - 2) < 1e-9
  assert abs(est.estimate_turns_to_sum(1200) - 3) < 1e-9

def linear_fit_estimator_test3(est):
  steps = random.randint(3, 1000)

  est.push(0)
  for i in xrange(steps):
    est.push(i + 1)
    assert abs(est.estimate() - (i + 2)) < 1e-9

def test_linear_fit_estimator():
  est = LinearFitEstimator()
  linear_fit_estimator_test1(est)

  est = LinearFitEstimator()
  linear_fit_estimator_test2(est)

  est = LinearFitEstimator()
  linear_fit_estimator_test3(est)

def test_limited_horizon_linear_fit_estimator():
  est = LimitedHorizonLinearFitEstimator(5)
  linear_fit_estimator_test1(est)

  est = LimitedHorizonLinearFitEstimator(5)
  linear_fit_estimator_test2(est)

  est = LimitedHorizonLinearFitEstimator(5)
  linear_fit_estimator_test3(est)
