import numpy as np
from numpy import asarray, newaxis, atleast_1d, ones, linspace, meshgrid
from numpy.linalg import norm


def ball_projection(c, x, r=1.0):
    """
    Projection integral of (d+1)-dimensional balls centered at c in given grid d-dim grid x.

    Parameters
    ----------
    c: array-like
        n d-dim center positions in `(n, d)` shape
    x: array
        Dense mesh grid defining position values in each dimension. Shape need to be `(d, x_1, x_2, ..., x_d)`, e.g.
        `(2, 512, 512)` for a 512x512 2-dim. grid.
    r: float, array-like, Optional
        Radii or scalar radius for balls to project.

    Returns
    -------
    balls: array
        Image with unit-density balls projected at given positions. Shape is same of x.shape[1:]

    Example
    ------

    >>> from hotopy.utils import gridn
    >>> from hotopy.image import ball_projection
    >>> from matplotlib import pyplot as plt
    >>> dims, L = (512, 600), 10
    >>> xx = gridn(dims) * L  # grid from [-5, 5] in each dim
    >>> img = ball_projection([[0, -2], [0, 2]], xx, r=0.5)  # note: positions in [y, x] if used with plt.imshow
    >>> plt.figure(); plt.imshow(img, extent=(-L/2, L/2, -L/2, L/2))
    """
    c = asarray(c)
    ndim = len(x)
    if c.ndim == 1 and c.shape[0] == ndim:
        c = c[np.newaxis, ...]
    s = (...,) + ndim * (newaxis,)
    xnorm = np.square(norm(x[newaxis] - c[s], axis=1))

    return np.sum(np.sqrt(np.maximum(0, r**2 - xnorm)) / r, axis=0)


def ndgaussian(n, sigma, c=None):
    """
    n-dimensional Gaussian with variance sigma, centered at c.

    Parameters
    ----------
    n: tuple
        shape of Gaussian
    sigma: float, array-like
        variance for all dims or per dim
    c: list, array-like
          center coordinate of the Gaussian. Defaults to ``len(n) * [0,]``.

    Notes
    -----
    For centered Gaussians (c=None) and scalar sigma this function is equivalent to
    ``ndwindow(("gaussian", sigma), n)``
    """
    n = atleast_1d(n)
    sigma = atleast_1d(sigma) * ones(len(n))
    if c is None:
        c = len(n) * [0]

    xv = [linspace(-ni / 2, ni / 2, ni, False) for ni in n]
    xx = meshgrid(*xv, indexing="ij")

    e = [(xi - ci) ** 2 / (2 * si**2) for xi, si, ci in zip(xx, sigma, c, strict=True)]
    f = np.exp(-np.sum(e, axis=0))

    return f


def ball(shape, radius, *, center=None):
    """
    n-dimensional ellipsoid

    Parameters
    ----------
    n: tuple
        shape of the image
    radius: float, array-like
        radius for all dims or per dim
    center: list, array-like
          center coordinate of the Gaussian. Defaults to ``shape/2``.

    """
    if center is None:
        center = np.atleast_1d(shape) / 2 - 0.5
    else:
        center = np.broadcast_to(center, len(shape))
    radius = np.broadcast_to(radius, len(shape))

    xsq = [((np.arange(s) - c) / r) ** 2 for s, c, r in zip(shape, center, radius, strict=True)]
    xsq = np.stack(np.meshgrid(*xsq, sparse=False, indexing="ij"))
    return np.sum(xsq, axis=0) <= 1


def get_lattice(xy, g, b, offset=0.0):
    """
    Generate n-dim lattice with lattice spacing g and width b on grid xy.

    Parameters
    ----------
    xy: array_like
        Dense meshgrid to use as coordinates.
    g: float, Tuple[float]
        Lattice constants per dimension. Scalar for a square lattice.
    b: float, Tuple[float]
        Lattice width per dimension. Scalar for a square lattice.
    offset: float, Tuple[float]
        Offset of lattice to start.

    Returns
    -------
    Lattice on xy grid.

    Example
    -------
    Generate grid

    >>> import numpy as np
    >>> from hotopy.image import get_lattice
    >>> xy = np.mgrid[-0.5:0.5:0.001, -0.5:0.5:0.001]  # unit grid with 1000 x 1000 points

    Simple lattice with ``b = 0.2`` spacing and 0.1 width (duty cycle of ``dc = 0.5``)

    >>> g, dc = 0.2, 0.5
    >>> l1 = get_lattice(xy, g, g * dc)

    Rotated lattice: Here we define a 2-dim rotation matrix ``R`` that rotates the cooridnated by 10° using a matrix
    product (``np.matmul``, note here in the first two dimensions) and finally generate the lattice on the rotated
    cooridnates.

    >>> def rot_2d(phi):
    ...     s, c = np.sin(phi), np.cos(phi)
    ...     return np.asarray([[c, s], [-s, c]])
    >>> R = rot_2d(np.deg2rad(10))
    >>> rxy = np.matmul(R, xy, axes=[(0,1)] * 3)
    >>> l2 = get_lattice(rxy, g, g * 0.2)
    """
    ndim = len(xy)
    g = np.broadcast_to(g, ndim)
    b = np.broadcast_to(b, ndim)
    offset = np.broadcast_to(offset, ndim)

    if np.any(b > g):
        raise ValueError("Width of lattice larger than lattice spacing.")

    return np.prod([np.mod(xy[i] - offset[i], g[i] or 1) >= b[i] for i in range(ndim)], axis=0)
