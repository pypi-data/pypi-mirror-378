import numpy as np
from sklearn.utils.validation import validate_data

from ._base import _PLSFeatureSelectorBase


class SRSelector(_PLSFeatureSelectorBase):
    """
    This selector is used to select features that contribute significantly
    to the latent variables in a PLS regression model using the Selectivity
    Ratio (SR) method.

    Parameters
    ----------
    - model: Union[_PLS, Pipeline]
        The PLS regression model or a pipeline with a PLS regression model as last step.

    - threshold: float, default=1.0
        The threshold for feature selection. Features with importance
        above this threshold will be selected.

    Attributes
    ----------
    estimator_ : ModelTypes
        The fitted model of type _BasePCA or _PLS

    feature_scores_ : np.ndarray
        The calculated feature scores based on the selected method.

    support_mask_ : np.ndarray
        The boolean mask indicating which features are selected.

    Methods
    -------
    fit(X, y=None)
        Fit the transformer to the input data. It calculates the feature scores and the feature_mask.
    """

    def __init__(
        self,
        model,
        threshold: float = 1.0,
    ):
        self.model = model
        self.threshold = threshold
        super().__init__(self.model)

    def fit(self, X: np.ndarray, y=None) -> "SRSelector":
        """
        Fit the transformer to calculate the feature scores and the support mask.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The input data to fit the transformer to.

        y : None
            Ignored.

        Returns
        -------
        self : SRSelector
            The fitted transformer.
        """
        # Check that X is a 2D array and has only finite values
        X = validate_data(
            self, X, y="no_validation", ensure_2d=True, reset=True, dtype=np.float64
        )

        # Calculate the SR scores
        self.feature_scores_ = self._calculate_features(X)

        # Calculate the support mask
        self.support_mask_ = self._get_support_mask()

        return self

    def _get_support_mask(self) -> np.ndarray:
        """
        Get the support mask based on the feature scores and threshold.
        Features with scores above the threshold are selected.
        Parameters
        ----------
        self : SRSelector
            The fitted transformer.

        Returns
        -------
        support_mask_ : np.ndarray
            The boolean mask indicating which features are selected.
        """
        return self.feature_scores_ > self.threshold

    def _calculate_features(self, X: np.ndarray) -> np.ndarray:
        """
        Vectorized Selectivity Ratio calculation from a fitted _PLS
        like model.

        Parameters:
        ----------
        - self: SRSelector
            The fitted transformer.

        - X: array-like of shape (n_samples, n_features)
            The input training data to calculate the feature scores from.

        Returns
        -------
        feature_scores_ : np.ndarray
            The calculated feature scores based on the selected method.
        """
        bpls = self.estimator_.coef_
        bpls_norm = bpls.T / np.linalg.norm(bpls)

        # Handle 1D case correctly
        if bpls.ndim == 1:
            bpls_norm = bpls_norm.reshape(-1, 1)

        # Project X onto the regression vector
        ttp = X @ bpls_norm
        ptp = X.T @ np.linalg.pinv(ttp).T

        # Predicted part of X
        X_hat = ttp @ ptp.T

        # Compute squared norms directly
        total_ss = np.linalg.norm(X, axis=0) ** 2
        explained_ss = np.linalg.norm(X_hat, axis=0) ** 2

        # Calculate residual sum of squares
        residual_ss = total_ss - explained_ss

        # Stability: avoid division by zero
        epsilon = 1e-12

        # Calculate Selectivity Ratio
        return explained_ss / (residual_ss + epsilon)
