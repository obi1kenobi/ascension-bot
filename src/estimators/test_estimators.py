import random
from estimators import AverageEstimator, WeightedAverageEstimator, LinearFitEstimator

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
    

def test_linear_fit_estimator():
    est = LinearFitEstimator()
    rand_number = random.randint(-100, 100)

    for i in xrange(100):
        est.push(rand_number)

    assert abs(est.estimate() - rand_number) < 1e-9



    est = LinearFitEstimator()
    est.push(100)
    est.push(200)
    assert abs(est.estimate() - 300) < 1e-9



    est = LinearFitEstimator()
    steps = random.randint(3, 1000)

    est.push(0)
    for i in xrange(steps):
        est.push(i + 1)
        assert abs(est.estimate() - (i + 2)) < 1e-9
