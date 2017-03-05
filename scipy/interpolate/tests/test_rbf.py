# Created by John Travers, Robert Hetland, 2007
""" Test functions for rbf module """
from __future__ import division, print_function, absolute_import


import numpy as np
from numpy.testing import (assert_, assert_array_almost_equal,
                           assert_almost_equal, run_module_suite)
from numpy import linspace, sin, random, exp, allclose
from scipy.interpolate.rbf import Rbf

FUNCTIONS = ('multiquadric', 'inverse multiquadric', 'gaussian',
             'cubic', 'quintic', 'thin-plate', 'linear')


def check_rbf1d_interpolation(function, degree):
    # Check that the Rbf function interpolates through the nodes (1D)
    x = linspace(0,10,9)
    y = sin(x)
    rbf = Rbf(x, y, function=function, degree=degree)
    yi = rbf(x)
    assert_array_almost_equal(y, yi)
    assert_almost_equal(rbf(float(x[0])), y[0])


def check_rbf2d_interpolation(function, degree):
    # Check that the Rbf function interpolates through the nodes (2D).
    x = random.rand(50,1)*4-2
    y = random.rand(50,1)*4-2
    z = x*exp(-x**2-1j*y**2)
    rbf = Rbf(x, y, z, epsilon=2, function=function, degree=degree)
    zi = rbf(x, y)
    zi.shape = x.shape
    assert_array_almost_equal(z, zi)


def check_rbf3d_interpolation(function, degree):
    # Check that the Rbf function interpolates through the nodes (3D).
    x = random.rand(50, 1)*4 - 2
    y = random.rand(50, 1)*4 - 2
    z = random.rand(50, 1)*4 - 2
    d = x*exp(-x**2 - y**2)
    rbf = Rbf(x, y, z, d, epsilon=2, function=function, degree=degree)
    di = rbf(x, y, z)
    di.shape = x.shape
    assert_array_almost_equal(di, d)


def test_rbf_interpolation():
    for function in FUNCTIONS:
        for degree in [None] + list(range(3)):
            yield check_rbf1d_interpolation, function, degree
            yield check_rbf2d_interpolation, function, degree
            yield check_rbf3d_interpolation, function, degree


def check_rbf1d_regularity(function, atol, degree):
    # Check that the Rbf function approximates a smooth function well away
    # from the nodes.
    x = linspace(0, 10, 9)
    y = sin(x)
    rbf = Rbf(x, y, function=function, degree=degree)
    xi = linspace(0, 10, 100)
    yi = rbf(xi)
    # import matplotlib.pyplot as plt
    # plt.figure()
    # plt.plot(x, y, 'o', xi, sin(xi), ':', xi, yi, '-')
    # plt.plot(x, y, 'o', xi, yi-sin(xi), ':')
    # plt.title(function)
    # plt.show()
    msg = "abs-diff: %f" % abs(yi - sin(xi)).max()
    assert_(allclose(yi, sin(xi), atol=atol), msg)


def test_rbf_regularity():
    tolerances = {
        'multiquadric': 0.1,
        'inverse multiquadric': 0.15,
        'gaussian': 0.15,
        'cubic': 0.15,
        'quintic': 0.1,
        'thin-plate': 0.1,
        'linear': 0.2
    }
    for function in FUNCTIONS:
        for degree in [None] + list(range(3)):
            yield check_rbf1d_regularity, function, tolerances.get(function, 1e-2), degree


def check_rbf1d_stability(function, degree):
    # Check that the Rbf function with default epsilon is not subject
    # to overshoot.  Regression for issue #4523.
    #
    # Generate some data (fixed random seed hence deterministic)
    np.random.seed(1234)
    x = np.linspace(0, 10, 50)
    z = x + 4.0 * np.random.randn(len(x))

    rbf = Rbf(x, z, function=function, degree=degree)
    xi = np.linspace(0, 10, 1000)
    yi = rbf(xi)

    # subtract the linear trend and make sure there no spikes
    assert_(np.abs(yi-xi).max() / np.abs(z-x).max() < 1.1)

def test_rbf_stability():
    for function in FUNCTIONS:
        for degree in [None] + list(range(3)):
            yield check_rbf1d_stability, function, degree


def test_default_construction():
    # Check that the Rbf class can be constructed with the default
    # multiquadric basis function. Regression test for ticket #1228.
    x = linspace(0,10,9)
    y = sin(x)
    rbf = Rbf(x, y)
    yi = rbf(x)
    assert_array_almost_equal(y, yi)


def test_function_is_callable():
    # Check that the Rbf class can be constructed with function=callable.
    x = linspace(0,10,9)
    y = sin(x)
    linfunc = lambda x:x
    rbf = Rbf(x, y, function=linfunc)
    yi = rbf(x)
    assert_array_almost_equal(y, yi)


def test_two_arg_function_is_callable():
    # Check that the Rbf class can be constructed with a two argument
    # function=callable.
    def _func(self, r):
        return self.epsilon + r

    x = linspace(0,10,9)
    y = sin(x)
    rbf = Rbf(x, y, function=_func)
    yi = rbf(x)
    assert_array_almost_equal(y, yi)


def test_rbf_epsilon_none():
    x = linspace(0, 10, 9)
    y = sin(x)
    Rbf(x, y, epsilon=None)


def test_rbf_epsilon_none_collinear():
    # Check that collinear points in one dimension doesn't cause an error
    # due to epsilon = 0
    x = [1, 2, 3]
    y = [4, 4, 4]
    z = [5, 6, 7]
    rbf = Rbf(x, y, z, epsilon=None)
    assert_(rbf.epsilon > 0)

if __name__ == "__main__":
    run_module_suite()
