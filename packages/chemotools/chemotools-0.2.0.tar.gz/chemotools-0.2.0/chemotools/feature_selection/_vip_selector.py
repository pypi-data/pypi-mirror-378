import numpy as np
from sklearn.utils.validation import validate_data

from ._base import _PLSFeatureSelectorBase


class VIPSelector(_PLSFeatureSelectorBase):
    """
    This selector is used to select features that contribute significantly
    to the latent variables in a PLS regression model using the Variables
    Importance in Projection (VIP) method.

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

    def fit(self, X: np.ndarray, y=None) -> "VIPSelector":
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
        self : VIPSelector
            The fitted transformer.
        """
        # Check that X is a 2D array and has only finite values
        X = validate_data(
            self, X, y="no_validation", ensure_2d=True, reset=True, dtype=np.float64
        )

        # Calculate the VIP scores
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
        self : VIPSelector
            The fitted transformer.

        Returns
        -------
        support_mask_ : np.ndarray
            The boolean mask indicating which features are selected.
        """
        return self.feature_scores_ > self.threshold

    def _calculate_features(self, X: np.ndarray) -> np.ndarray:
        """
        Calculate the VIP scores based on the fitted model.

        Parameters
        ----------
        self : VIPSelector
            The fitted transformer.

        Returns
        -------
        feature_scores_ : np.ndarray
            The calculated feature scores based on the selected method.
        """
        # Calculate sum of squares of y_loadings and x_scores
        sum_of_squares_y_loadings = (
            np.linalg.norm(self.estimator_.y_loadings_, ord=2, axis=0) ** 2
        )
        sum_of_squares_x_scores = (
            np.linalg.norm(self.estimator_.x_scores_, ord=2, axis=0) ** 2
        )

        # Calculate the sum of squares
        sum_of_squares = sum_of_squares_y_loadings * sum_of_squares_x_scores

        # Calculate the numerator
        numerator = self.estimator_.n_features_in_ * np.sum(
            sum_of_squares * self.estimator_.x_weights_**2,
            axis=1,
        )

        # Calculate the denominator
        denominator = np.sum(sum_of_squares, axis=0)

        # Calculate the VIP scores
        return np.sqrt(numerator / denominator)
