import numpy as np
import torch
from torch import fft

from .constraints import ConstraintOperator
from .regularization import twolevel_regularization
from .propagation import phase_chirp, expand_fresnel_numbers
from ..optimize import RestartADMM


class ICT:
    r"""
    Callable `Intensity contrast transfer` (ICT) phase reconstruction method based on [1]_.

    The reconstructions is the Tikhonov-regularized linear least squares solution (closed form):

    .. math::
        \phi_* = \frac{\delta}{2\beta}\ln
                \mathcal{F}^{-1} \left[ \left( H^\top H + \alpha \right)^{-1} H^\top \mathcal{F}I \right]

    Parameters
    ----------
    shape: tuple
        Image dimensions of holograms to reconstruct excluding multi-distance stack.
    fresnel_num: float, array_like
        (List of) Pixel Fresnel numbers of the given holograms.
    betadelta: float
        Homogeneous object assumption: proportionality factor between absorption and phase shift in complex refractive index. Needs to be strictly
        larger than zero :math:`\frac{\beta}{\delta} > 0`.
    alpha: float, tuple, Optional
        Regularization value. Can either be a single scalar to be constant over all frequencies or 2-tuple
        `(alpha_low, alpha_high)` with different values to low and high frequencies. Defaults to 0, no regularization.
    device: torch.device, Optional
        Device to perform computations on.
    dtype: torch.dtype, Optional
        Datatype to cast kernel into.

    Returns
    -------
    f: Callable
        Callable reconstruction function. Apply to hologram ``y`` with ``f(y)``.

    See also
    --------
    CTF
    Tikhonov
    ModifiedBronnikov

    References
    ----------
    .. [1]
        T. Faragó, R. Spiecker, M. Hurst, M. Zuber, A. Cecilia, and T. Baumbach,
        "Phase retrieval in propagation-based X-ray imaging beyond the limits of transport of intensity and contrast
        transfer function approaches," Opt. Lett.  49, 5159-5162 (2024).
        :doi:`10.1364/OL.530330`
    """

    def __init__(self, shape, fresnel_nums, betadelta, alpha=0.0, device=None, dtype=None):
        self.shape = shape = tuple(np.atleast_1d(shape))
        self.ndim = len(shape)
        self.device = device
        self.dtype = dtype
        self.stack_axis = -self.ndim - 1

        if self.ndim != 2:
            raise NotImplementedError(
                f"{self.__class__.__name__} only implemented for 2-dim images."
            )
        if not betadelta > 0:
            raise ValueError(
                f"{self.__class__.__name__}: {betadelta = :} needs to be strictly larger than zero."
            )

        # apply twolevel regularization if alpha in ``(alpha_low, alpha_high)`` notation, same as in CTF
        if np.size(alpha) == 2:
            alpha = twolevel_regularization(shape, fresnel_nums, alpha)

        self._deltabeta2 = 1.0 / betadelta / 2
        fresnel_nums = expand_fresnel_numbers(fresnel_nums, ndim=self.ndim)
        chi = phase_chirp(shape, fresnel_nums)
        A = np.cos(chi) + 1.0 / betadelta * np.sin(chi)
        AtA = (A**2).sum(self.stack_axis) + alpha

        self.A = torch.asarray(A, device=device, dtype=dtype)
        self.AtA = torch.asarray(AtA, device=device, dtype=dtype)

    def apply(self, holos):
        b = torch.as_tensor(holos, device=self.device)
        if holos.ndim == self.ndim:
            b = b[np.newaxis]  # add auxiliary axis to reduce later with sum operation
        B = fft.fft2(b)
        X = (self.A * B).sum(self.stack_axis) / self.AtA
        x = self._deltabeta2 * torch.log(fft.ifft2(X))
        return x.real

    def prox(self, holos):
        b = torch.as_tensor(holos, device=self.device)
        if holos.ndim == self.ndim:
            b = b[np.newaxis]  # add auxiliary axis to reduce later with sum operation
        B = fft.fft2(b)
        Atb = (self.A * B).sum(self.stack_axis)

        def prox_op(y, t=0.0):
            y = torch.as_tensor(y, device=self.device)
            if y.ndim == self.ndim:
                y = y[np.newaxis]
            Y = fft.fft2(y)
            X = (Atb + t * Y) / (self.AtA + t)
            x = self._deltabeta2 * torch.log(fft.ifft2(X))
            return x.real

        return prox_op

    def constrained(self, holos, constraints, tau=None, eta=None):
        if tau is None:
            tau = 1e-2  # default step size

        prox_ict = self.prox(holos)

        if isinstance(constraints, ConstraintOperator):
            constraints.to_device(self.device)

        x = torch.zeros(self.shape, dtype=self.dtype, device=self.device)
        z = torch.zeros_like(x)
        solver = RestartADMM(x, z, prox_ict, constraints, tau=tau, eta=eta, device=self.device)

        return solver

    def __call__(self, holos, constraints=None, max_iter=100, tol=1e-3, tau=None, eta=None):
        if constraints is None:
            # unconstrained: least squares solution (closed form)
            return self.apply(holos)

        # else: with constraints: use iterative ADMM scheme to minimize distance
        # between proximal least squares of A and constraints
        solver = self.constrained(holos, constraints)

        # solve iteratively
        solver(max_iter=max_iter, tol=tol)
        x_rec = solver.u[0]

        return x_rec
