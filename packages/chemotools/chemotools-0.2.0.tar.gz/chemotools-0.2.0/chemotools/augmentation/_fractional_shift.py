from typing import Literal, Optional
import numpy as np
from scipy.interpolate import CubicSpline
from scipy import stats
from sklearn.base import BaseEstimator, TransformerMixin, OneToOneFeatureMixin
from sklearn.utils import check_random_state
from sklearn.utils.validation import check_is_fitted, validate_data
from sklearn.utils._param_validation import Interval, Real, StrOptions


class FractionalShift(TransformerMixin, OneToOneFeatureMixin, BaseEstimator):
    """
    Shift signals by a random fractional amount using cubic spline interpolation.

    Parameters
    ----------
    shift : float, default=0.0
        Maximum absolute shift applied to each signal.
        A random shift is drawn uniformly from [-shift, +shift].

    padding_mode : {'zeros', 'constant', 'wrap', 'extend', 'mirror', 'linear'}, default='linear'
        Padding strategy for extrapolated values.

    pad_value : float, default=0.0
        Used when `padding_mode='constant'`.

    random_state : int, RandomState instance or None, default=None
        Controls randomness.
    """

    _parameter_constraints: dict = {
        "shift": [Interval(Real, 0, None, closed="both")],
        "padding_mode": [
            StrOptions({"zeros", "constant", "extend", "mirror", "linear"})
        ],
        "pad_value": [Real],
        "random_state": [None, int, np.random.RandomState],
    }

    def __init__(
        self,
        shift: float = 0.0,
        padding_mode: Literal[
            "zeros", "constant", "extend", "mirror", "linear"
        ] = "linear",
        pad_value: float = 0.0,
        random_state: Optional[int] = None,
    ):
        self.shift = shift
        self.padding_mode = padding_mode
        self.pad_value = pad_value
        self.random_state = random_state

    def fit(self, X, y=None):
        X = validate_data(
            self, X, y="no_validation", ensure_2d=True, reset=True, dtype=np.float64
        )
        self._rng = check_random_state(self.random_state)
        return self

    def transform(self, X, y=None):
        check_is_fitted(self, "n_features_in_")
        X = validate_data(
            self,
            X,
            y="no_validation",
            ensure_2d=True,
            copy=True,
            reset=False,
            dtype=np.float64,
        )
        return np.array([self._shift_signal(x) for x in X])

    def _shift_signal(self, x):
        n = len(x)
        shift = self._rng.uniform(-self.shift, self.shift)
        indices = np.arange(n)
        shifted_indices = indices + shift

        spline = CubicSpline(indices, x, bc_type="not-a-knot")
        shifted = spline(shifted_indices)

        # handle padding
        if self.padding_mode == "zeros":
            shifted[shifted_indices < 0] = 0
            shifted[shifted_indices >= n - 1] = 0
        elif self.padding_mode == "constant":
            shifted[shifted_indices < 0] = self.pad_value
            shifted[shifted_indices >= n - 1] = self.pad_value
        elif self.padding_mode == "extend":
            shifted[shifted_indices < 0] = x[0]
            shifted[shifted_indices >= n - 1] = x[-1]
        elif self.padding_mode == "mirror":
            shifted = self._apply_mirror_padding(x, shifted, shifted_indices)
        elif self.padding_mode == "linear":
            shifted = self._apply_linear_padding(x, shifted, shifted_indices)
        return shifted

    # --- helper methods ---
    def _apply_mirror_padding(self, x, shifted, shifted_indices):
        n = len(x)
        left_len = np.sum(shifted_indices < 0)
        right_len = np.sum(shifted_indices >= n - 1)
        if left_len > 0:
            pad = np.tile(x[1:][::-1], int(np.ceil(left_len / (n - 1))))[:left_len]
            shifted[shifted_indices < 0] = pad
        if right_len > 0:
            pad = np.tile(x[:-1][::-1], int(np.ceil(right_len / (n - 1))))[:right_len]
            shifted[shifted_indices >= n - 1] = pad
        return shifted

    def _apply_linear_padding(self, x, shifted, shifted_indices):
        n = len(x)
        left_len = np.sum(shifted_indices < 0)
        right_len = np.sum(shifted_indices >= n - 1)

        if left_len > 0:
            points = x[: min(5, n)]
            slope, intercept, *_ = stats.linregress(np.arange(len(points)), points)
            new_x = np.arange(-left_len, 0)
            shifted[shifted_indices < 0] = slope * new_x + intercept

        if right_len > 0:
            points = x[-min(5, n) :]
            slope, intercept, *_ = stats.linregress(np.arange(len(points)), points)
            new_x = np.arange(len(points), len(points) + right_len)
            shifted[shifted_indices >= n - 1] = slope * new_x + intercept

        return shifted
