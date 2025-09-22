import numpy as np
from scipy.linalg import circulant
from scipy.optimize import curve_fit, brentq
from scipy.interpolate import interp1d

from abel import _deprecate


def gradient(f, x=None, dx=1, axis=-1):
    """
    Return the gradient of 1 or 2-dimensional array.
    The gradient is computed using central differences in the interior
    and first differences at the boundaries.

    Irregular sampling is supported (it isn't supported by np.gradient)

    Parameters
    ----------
    f : 1d or 2d numpy array
        Input array.
    x : array_like, optional
       Points where the function f is evaluated. It must be of the same
       length as ``f.shape[axis]``.
       If None, regular sampling is assumed (see dx)
    dx : float, optional
       If `x` is None, spacing given by `dx` is assumed. Default is 1.
    axis : int, optional
       The axis along which the difference is taken.

    Returns
    -------
    out : array_like
        Returns the gradient along the given axis.

    Notes
    -----
    To-Do: implement smooth noise-robust differentiators for use on experimental data.
    http://www.holoborodko.com/pavel/numerical-methods/numerical-derivative/smooth-low-noise-differentiators/
    """

    if x is None:
        x = np.arange(f.shape[axis]) * dx
    else:
        assert x.shape[0] == f.shape[axis]
    I = np.zeros(f.shape[axis])
    I[:2] = np.array([0, -1])
    I[-1] = 1
    I = circulant(I)
    I[0, 0] = -1
    I[-1, -1] = 1
    I[0, -1] = 0
    I[-1, 0] = 0
    H = np.zeros((f.shape[axis], 1))
    H[1:-1, 0] = x[2:] - x[:-2]
    H[0] = x[1] - x[0]
    H[-1] = x[-1] - x[-2]
    if axis == 0:
        return np.dot(I / H, f)
    else:
        return np.dot(I / H, f.T).T


def gaussian(x, a, mu, sigma, c):
    r"""
    `Gaussian function <https://en.wikipedia.org/wiki/Gaussian_function>`_

    :math:`f(x)=a e^{-(x - \mu)^2 / (2 \sigma^2)} + c`

    Parameters
    ----------
    x : 1D np.array
        coordinate

    a : float
        the height of the curve's peak

    mu : float
        the position of the center of the peak

    sigma : float
        the standard deviation, sometimes called the Gaussian RMS width

    c : float
        non-zero background

    Returns
    -------
    out : 1D np.array
        the Gaussian profile
    """
    return a * np.exp(-((x - mu) ** 2) / 2 / sigma ** 2) + c


def guess_gaussian(x):
    """
    Find a set of better starting parameters for Gaussian function fitting

    Parameters
    ----------
    x : 1D np.array
        1D profile of your data

    Returns
    -------
    out : tuple of float
        estimated value of (a, mu, sigma, c)
    """
    c_guess = (x[0] + x[-1]) / 2
    a_guess = x.max() - c_guess
    mu_guess = x.argmax()
    x_inter = interp1d(range(len(x)), x)

    def _(i):
        return x_inter(i) - a_guess / 2 - c_guess

    try:
        sigma_l_guess = brentq(_, 0, mu_guess)
    except ValueError:
        sigma_l_guess = len(x) / 4
    try:
        sigma_r_guess = brentq(_, mu_guess, len(x) - 1)
    except ValueError:
        sigma_r_guess = 3 * len(x) / 4
    return a_guess, mu_guess, (sigma_r_guess -
                               sigma_l_guess) / 2.35482, c_guess


def fit_gaussian(x):
    """
    Fit a Gaussian function to x and return its parameters

    Parameters
    ----------
    x : 1D np.array
        1D profile of your data

    Returns
    -------
    out : tuple of float
        (a, mu, sigma, c)
    """
    res = curve_fit(gaussian, np.arange(x.size), x, p0=guess_gaussian(x),
                    method='trf')  # default 'lm' is broken, see Scipy #21995
    return res[0]  # extract optimal values


def guss_gaussian(x):
    """Deprecated function. Use :func:`guess_gaussian` instead."""
    _deprecate('abel.tools.math.guss_gaussian() is renamed to '
               '...guess_gaussian(), please update your code.')
    return guess_gaussian(x)
