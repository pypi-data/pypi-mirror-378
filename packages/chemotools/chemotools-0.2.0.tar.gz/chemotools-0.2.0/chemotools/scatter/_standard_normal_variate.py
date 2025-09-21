"""
The :mod:`chemotools.scatter._standard_normal_variate` module implements the Standard Normal Variate (SNV) transformation.
"""

# Authors: Pau Cabaneros
# License: MIT

import warnings
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin, OneToOneFeatureMixin
from sklearn.utils.validation import check_is_fitted, validate_data


class StandardNormalVariate(TransformerMixin, OneToOneFeatureMixin, BaseEstimator):
    """
    A transformer that calculates the standard normal variate of the input data.

    Methods
    -------
    fit(X, y=None)
        Fit the transformer to the input data.

    transform(X, y=0, copy=True)
        Transform the input data by calculating the standard normal variate.

    _calculate_standard_normal_variate(x)
        Calculate the standard normal variate for a single spectrum.

    Raises
    ------
    UserWarning
        If the standard deviation of a spectrum is zero (spectrum is flat), a warning is raised
        indicating that the result will contain NaNs.

    Examples
    --------
    >>> from chemotools.scatter import StandardNormalVariate
    >>> import numpy as np
    >>> X = np.array([[1, 2, 3, 4, 5]])
    >>> snv = StandardNormalVariate()
    >>> X_transformed = snv.fit_transform(X)

    References
    ----------
    [1] Åsmund Rinnan, Frans van den Berg, Søren Balling Engelsen,
        "Review of the most common pre-processing techniques for near-infrared spectra,"
        TrAC Trends in Analytical Chemistry 28 (10) 1201-1222 (2009).
    """

    def fit(self, X: np.ndarray, y=None) -> "StandardNormalVariate":
        """
        Fit the transformer to the input data.

        Parameters
        ----------
        X : np.ndarray of shape (n_samples, n_features)
            The input data to fit the transformer to.

        y : None
            Ignored.

        Returns
        -------
        self : StandardNormalVariate
            The fitted transformer.
        """
        # Check that X is a 2D array and has only finite values
        X = validate_data(
            self, X, y="no_validation", ensure_2d=True, reset=True, dtype=np.float64
        )
        return self

    def transform(self, X: np.ndarray, y=None) -> np.ndarray:
        """
        Transform the input data by calculating the standard normal variate.

        Parameters
        ----------
        X : np.ndarray of shape (n_samples, n_features)
            The input data to transform.

        y : None
            Ignored.

        Returns
        -------
        X_ : np.ndarray of shape (n_samples, n_features)
            The transformed data.
        """
        # Check that the estimator is fitted
        check_is_fitted(self, "n_features_in_")

        # Check that X is a 2D array and has only finite values
        X_ = validate_data(
            self,
            X,
            y="no_validation",
            ensure_2d=True,
            copy=True,
            reset=False,
            dtype=np.float64,
        )

        # Calculate the standard normal variate
        for i, x in enumerate(X_):
            X_[i] = self._calculate_standard_normal_variate(x)

        return X_.reshape(-1, 1) if X_.ndim == 1 else X_

    def _calculate_standard_normal_variate(self, x) -> np.ndarray:
        std = x.std()
        if std == 0:
            warnings.warn(
                "Standard deviation is zero in SNV. This indicates a flat signal and will result in NaNs.",
                UserWarning,
                stacklevel=2,
            )
        return (x - x.mean()) / std
