# !/usr/bin/env python
# Created by "Matt Q." at 23:05, 27/10/2022 --------%
#       Github: https://github.com/N3uralN3twork    %
#                                                   %
# Improved by: "Thieu" at 11:45, 25/07/2023 --------%
#       Email: nguyenthieu2102@gmail.com            %
#       Github: https://github.com/thieu1995        %
# --------------------------------------------------%
import time

import numpy as np
from permetrics.evaluator import Evaluator
from permetrics.utils import data_util as du
from permetrics.utils import cluster_util as cu


class ClusteringMetric(Evaluator):
    """
    Defines a ClusteringMetric class that hold all internal and external metrics for clustering problems

    + An extension of scikit-learn metrics section, with the addition of many more internal metrics.
    + https://scikit-learn.org/stable/modules/clustering.html#clustering-evaluation

    Parameters
    ----------
    y_true: tuple, list, np.ndarray, default = None
        The ground truth values. This is for calculating external metrics

    y_pred: tuple, list, np.ndarray, default = None
        The prediction values. This is for both calculating internal and external metrics

    X: tuple, list, np.ndarray, default = None
        The features of datasets. This is for calculating internal metrics

    decimal: int, default = 5
        The number of fractional parts after the decimal point

    raise_error: bool, default = False
        Some metrics can't be calculate when some problems occur, show it will raise error as usual.
        We can return the biggest value or smallest value depend on metric instead of raising error.

    biggest_value: float, default = None
        The biggest value will be returned for metric that has min characteristic and ``raise_error=True``
        Default = None, then the value will be ``np.inf``.

    smallest_value: float, default = None
        The smallest value will be returned for metric that has max characteristic and ``raise_error=True``
        Default = None, then the value will be ``-np.inf``.
    """

    SUPPORT = {
        "BHI": {"type": "min", "range": "[0, +inf)", "best": "0"},
        "XBI": {"type": "min", "range": "[0, +inf)", "best": "0"},
        "DBI": {"type": "min", "range": "[0, +inf)", "best": "0"},
        "BRI": {"type": "min", "range": "(-inf, +inf)", "best": "no best"},
        "KDI": {"type": "min", "range": "(-inf, +inf)", "best": "no best"},
        "DRI": {"type": "max", "range": "[0, +inf)", "best": "no best"},
        "DI": {"type": "max", "range": "[0, +inf)", "best": "no best"},
        "CHI": {"type": "max", "range": "[0, +inf)", "best": "no best"},
        "LDRI": {"type": "max", "range": "(-inf, +inf)", "best": "no best"},
        "LSRI": {"type": "max", "range": "(-inf, +inf)", "best": "no best"},
        "SI": {"type": "max", "range": "[-1, +1]", "best": "1"},
        "SSEI": {"type": "min", "range": "[0, +inf)", "best": "0"},
        "DHI": {"type": "min", "range": "[0, +inf)", "best": "0"},
        "BI": {"type": "min", "range": "[0, +inf)", "best": "0"},
        "RSI": {"type": "max", "range": "(-inf, +1]", "best": "1"},
        "DBCVI": {"type": "min", "range": "[0, 1]", "best": "0"},
        "HI": {"type": "min", "range": "[0, +inf)", "best": "0"},
        "MIS": {"type": "max", "range": "[0, +inf)", "best": "no best"},
        "NMIS": {"type": "max", "range": "[0, 1]", "best": "1"},
        "RaS": {"type": "max", "range": "[0, 1]", "best": "1"},
        "FMS": {"type": "max", "range": "[0, 1]", "best": "1"},
        "HS": {"type": "max", "range": "[0, 1]", "best": "1"},
        "CS": {"type": "max", "range": "[0, 1]", "best": "1"},
        "VMS": {"type": "max", "range": "[0, 1]", "best": "1"},
        "PrS": {"type": "max", "range": "[0, 1]", "best": "1"},
        "ReS": {"type": "max", "range": "[0, 1]", "best": "1"},
        "FmS": {"type": "max", "range": "[0, 1]", "best": "1"},
        "CDS": {"type": "max", "range": "[0, 1]", "best": "1"},
        "HGS": {"type": "max", "range": "[-1, 1]", "best": "1"},
        "JS": {"type": "max", "range": "[0, 1]", "best": "1"},
        "KS": {"type": "max", "range": "[0, 1]", "best": "1"},
        "MNS": {"type": "max", "range": "(-inf, +inf)", "best": "no best"},
        "PhS": {"type": "max", "range": "(-inf, +inf)", "best": "no best"},
        "RTS": {"type": "max", "range": "[0, 1]", "best": "1"},
        "RRS": {"type": "max", "range": "[0, 1]", "best": "1"},
        "SS1S": {"type": "max", "range": "[0, 1]", "best": "1"},
        "SS2S": {"type": "max", "range": "[0, 1]", "best": "1"},
        "PuS": {"type": "max", "range": "[0, 1]", "best": "1"},
        "ES": {"type": "min", "range": "[0, 1]", "best": "0"},
        "TS": {"type": "max", "range": "[-1, +1]", "best": "1"},
    }

    def __init__(self, y_true=None, y_pred=None, X=None, decimal=5,
                 raise_error=False, biggest_value=None, smallest_value=None, **kwargs):
        super().__init__(y_true, y_pred, decimal, **kwargs)
        if kwargs is None: kwargs = {}
        self.set_keyword_arguments(kwargs)
        self.X = X
        self.le = None
        self.raise_error = raise_error
        self.biggest_value = np.inf if biggest_value is None else biggest_value
        self.smallest_value = -np.inf if smallest_value is None else smallest_value

    @staticmethod
    def get_support(name=None, verbose=True):
        if name == "all":
            if verbose:
                for key, value in ClusteringMetric.SUPPORT.items():
                    print(f"Metric {key} : {value}")
            return ClusteringMetric.SUPPORT
        if name not in list(ClusteringMetric.SUPPORT.keys()):
            raise ValueError(f"ClusteringMetric doesn't support metric named: {name}")
        else:
            if verbose:
                print(f"Metric {name}: {ClusteringMetric.SUPPORT[name]}")
            return ClusteringMetric.SUPPORT[name]

    def get_processed_external_data(self, y_true=None, y_pred=None, decimal=None):
        """
        Args:
            y_true (tuple, list, np.ndarray): The ground truth values
            y_pred (tuple, list, np.ndarray): The prediction values
            decimal (int, None): The number of fractional parts after the decimal point

        Returns:
            y_true_final: y_true used in evaluation process.
            y_pred_final: y_pred used in evaluation process
            le: label encoder object
            decimal: The number of fractional parts after the decimal point
        """
        decimal = self.decimal if decimal is None else decimal
        if y_pred is None:              # Check for function called
            if self.y_pred is None:     # Check for object of class called
                raise ValueError("You need to pass y_true and y_pred to calculate external clustering metrics.")
            else:
                if self.y_true is None:
                    # y_true, y_pred, self.le = format_internal_clustering_data(self.y_pred)
                    raise ValueError("You need to pass y_true and y_pred to calculate external clustering metrics.")
                else:
                    y_true, y_pred, self.le = du.format_external_clustering_data(self.y_true, self.y_pred)
        else:   # This is for function called, it will override object of class called
            if y_true is None:
                # y_true, y_pred, self.le = format_internal_clustering_data(y_pred)
                raise ValueError("You need to pass y_true and y_pred to calculate external clustering metrics.")
            else:
                y_true, y_pred, self.le = du.format_external_clustering_data(y_true, y_pred)
        return y_true, y_pred, self.le, decimal

    def get_processed_internal_data(self, y_pred=None, decimal=None):
        """
        Args:
            y_pred (tuple, list, np.ndarray): The prediction values
            decimal (int, None): The number of fractional parts after the decimal point

        Returns:
            y_pred_final: y_pred used in evaluation process
            le: label encoder object
            decimal: The number of fractional parts after the decimal point
        """
        decimal = self.decimal if decimal is None else decimal
        if y_pred is None:              # Check for function called
            if self.y_pred is None:     # Check for object of class called
                raise ValueError("You need to pass y_pred to calculate external clustering metrics.")
            else:
                y_pred, self.le = du.format_internal_clustering_data(self.y_pred)
        else:   # This is for function called, it will override object of class called
            y_pred, self.le = du.format_internal_clustering_data(y_pred)
        return y_pred, self.le, decimal

    def check_X(self, X):
        if X is None:
            if self.X is None:
                raise ValueError("To calculate internal metrics, you need to pass X.")
            else:
                return self.X
        return X

    def ball_hall_index(self, X=None, y_pred=None, decimal=None, **kwargs):
        """
        The Ball-Hall Index (1995) is the mean of the mean dispersion across all clusters.
        The **largest difference** between successive clustering levels indicates the optimal number of clusters.
        Smaller is better (Best = 0), Range=[0, +inf)

        Args:
            X (array-like of shape (n_samples, n_features)):
                A list of `n_features`-dimensional data points. Each row corresponds to a single data point.
            y_pred (array-like of shape (n_samples,)): Predicted labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Ball-Hall index
        """
        X = self.check_X(X)
        y_pred, _, decimal = self.get_processed_internal_data(y_pred, decimal)
        return cu.calculate_ball_hall_index(X, y_pred, decimal)

    def calinski_harabasz_index(self, X=None, y_pred=None, decimal=None, **kwargs):
        """
        Compute the Calinski and Harabasz (1974) index. It is also known as the Variance Ratio Criterion.
        The score is defined as ratio between the within-cluster dispersion and the between-cluster dispersion.
        Bigger is better (No best value), Range=[0, inf)

        Notes:
        ~~~~~~
            + This metric in scikit-learn library is wrong in calculate the intra_disp variable (WGSS)
            + https://github.com/scikit-learn/scikit-learn/blob/7f9bad99d/sklearn/metrics/cluster/_unsupervised.py#L351C1-L351C1

        Args:
            X (array-like of shape (n_samples, n_features)):
                A list of `n_features`-dimensional data points. Each row corresponds to a single data point.
            y_pred (array-like of shape (n_samples,)): Predicted labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The resulting Calinski-Harabasz index.
        """
        X = self.check_X(X)
        y_pred, _, decimal = self.get_processed_internal_data(y_pred, decimal)
        return cu.calculate_calinski_harabasz_index(X, y_pred, decimal, self.raise_error, 0.0)

    def xie_beni_index(self, X=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Xie-Beni index.
        Smaller is better (Best = 0), Range=[0, +inf)

        The Xie-Beni index is an index of fuzzy clustering, but it is also applicable to crisp clustering.
        The numerator is the mean of the squared distances of all of the points with respect to their
        barycenter of the cluster they belong to. The denominator is the minimal squared distances between
        the points in the clusters. The **minimum** value indicates the best number of clusters.

        Args:
            X (array-like of shape (n_samples, n_features)):
                A list of `n_features`-dimensional data points. Each row corresponds to a single data point.
            y_pred (array-like of shape (n_samples,)): Predicted labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Xie-Beni index
        """
        X = self.check_X(X)
        y_pred, _, decimal = self.get_processed_internal_data(y_pred, decimal)
        return cu.calculate_xie_beni_index(X, y_pred, decimal, self.raise_error, self.biggest_value)

    def banfeld_raftery_index(self, X=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Banfeld-Raftery Index.
        Smaller is better (No best value), Range=(-inf, inf)
        This index is the weighted sum of the logarithms of the traces of the variance covariance matrix of each cluster

        Args:
            X (array-like of shape (n_samples, n_features)):
                A list of `n_features`-dimensional data points. Each row corresponds to a single data point.
            y_pred (array-like of shape (n_samples,)): Predicted labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Banfeld-Raftery Index
        """
        X = self.check_X(X)
        y_pred, _, decimal = self.get_processed_internal_data(y_pred, decimal)
        return cu.calculate_banfeld_raftery_index(X, y_pred, decimal, self.raise_error, self.biggest_value)

    def davies_bouldin_index(self, X=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Davies-Bouldin index
        Smaller is better (Best = 0), Range=[0, +inf)

        Args:
            X (array-like of shape (n_samples, n_features)):
                A list of `n_features`-dimensional data points. Each row corresponds to a single data point.
            y_pred (array-like of shape (n_samples,)): Predicted labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Davies-Bouldin index
        """
        X = self.check_X(X)
        y_pred, _, decimal = self.get_processed_internal_data(y_pred, decimal)
        return cu.calculate_davies_bouldin_index(X, y_pred, decimal, self.raise_error, self.biggest_value)

    def det_ratio_index(self, X=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Det-Ratio index
        Bigger is better (No best value), Range=[0, +inf)

        Args:
            X (array-like of shape (n_samples, n_features)):
                A list of `n_features`-dimensional data points. Each row corresponds to a single data point.
            y_pred (array-like of shape (n_samples,)): Predicted labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Det-Ratio index
        """
        X = self.check_X(X)
        y_pred, _, decimal = self.get_processed_internal_data(y_pred, decimal)
        return cu.calculate_det_ratio_index(X, y_pred, decimal, self.raise_error, self.smallest_value)

    def dunn_index(self, X=None, y_pred=None, decimal=None, use_modified=True, **kwargs):
        """
        Computes the Dunn Index
        Bigger is better (No best value), Range=[0, +inf)

        Args:
            X (array-like of shape (n_samples, n_features)):
                A list of `n_features`-dimensional data points. Each row corresponds to a single data point.
            y_pred (array-like of shape (n_samples,)): Predicted labels for each sample.
            decimal (int): The number of fractional parts after the decimal point
            use_modified (bool): The modified version we proposed to speed up the computational time for this metric, default=True

        Returns:
            result (float): The Dunn Index
        """
        X = self.check_X(X)
        y_pred, _, decimal = self.get_processed_internal_data(y_pred, decimal)
        return cu.calculate_dunn_index(X, y_pred, decimal, use_modified, self.raise_error, 0.0)

    def ksq_detw_index(self, X=None, y_pred=None, decimal=None, use_normalized=True, **kwargs):
        """
        Computes the Ksq-DetW Index
        Smaller is better (No best value), Range=(-inf, +inf)

        Args:
            X (array-like of shape (n_samples, n_features)):
                A list of `n_features`-dimensional data points. Each row corresponds to a single data point.
            y_pred (array-like of shape (n_samples,)): Predicted labels for each sample.
            decimal (int): The number of fractional parts after the decimal point
            use_normalized (bool): We normalize the scatter matrix before calculate the Det to reduce the value, default=True

        Returns:
            result (float): The Ksq-DetW Index
        """
        X = self.check_X(X)
        y_pred, _, decimal = self.get_processed_internal_data(y_pred, decimal)
        return cu.calculate_ksq_detw_index(X, y_pred, decimal, use_normalized)

    def log_det_ratio_index(self, X=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Log Det Ratio Index
        Bigger is better (No best value), Range=(-inf, +inf)

        Args:
            X (array-like of shape (n_samples, n_features)):
                A list of `n_features`-dimensional data points. Each row corresponds to a single data point.
            y_pred (array-like of shape (n_samples,)): Predicted labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Log Det Ratio Index
        """
        X = self.check_X(X)
        y_pred, _, decimal = self.get_processed_internal_data(y_pred, decimal)
        return cu.calculate_log_det_ratio_index(X, y_pred, decimal, self.raise_error, self.smallest_value)

    def log_ss_ratio_index(self, X=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Log SS Ratio Index
        Bigger is better (No best value), Range=(-inf, +inf)

        Args:
            X (array-like of shape (n_samples, n_features)):
                A list of `n_features`-dimensional data points. Each row corresponds to a single data point.
            y_pred (array-like of shape (n_samples,)): Predicted labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Log SS Ratio Index
        """
        X = self.check_X(X)
        y_pred, _, decimal = self.get_processed_internal_data(y_pred, decimal)
        n_clusters = len(np.unique(y_pred))
        if n_clusters == 1:
            if self.raise_error:
                raise ValueError("The Log SS Ratio Index is undefined when y_pred has only 1 cluster.")
            else:
                return self.smallest_value
        centers, _ = cu.compute_barycenters(X, y_pred)
        bgss = cu.compute_BGSS(X, y_pred)
        wgss = cu.compute_WGSS(X, y_pred)
        return np.round(np.log(bgss/wgss), decimal)

    def silhouette_index(self, X=None, y_pred=None, decimal=None, multi_output=False, **kwarg):
        """
        Computes the Silhouette Index
        Higher is better (Best = 1), Range = [-1, +1]

        Args:
            X (array-like of shape (n_samples, n_features)):
                A list of `n_features`-dimensional data points. Each row corresponds to a single data point.
            y_pred (array-like of shape (n_samples,)): Predicted labels for each sample.
            decimal (int): The number of fractional parts after the decimal point
            multi_output (bool): Returned scores for each cluster, default=False

        Returns:
            result (float): The Silhouette Index
        """
        X = self.check_X(X)
        y_pred, _, decimal = self.get_processed_internal_data(y_pred, decimal)
        return cu.calculate_silhouette_index(X, y_pred, decimal, multi_output)

    def sum_squared_error_index(self, X=None, y_pred=None, decimal=None, **kwarg):
        """
        Computes the Sum of Squared Error Index
        Smaller is better (Best = 0), Range = [0, +inf)

        SSE measures the sum of squared distances between each data point and its corresponding centroid or cluster center.
        It quantifies the compactness of the clusters. Here's how you can calculate the SSE in a clustering problem:

            1) Assign each data point to its nearest centroid or cluster center based on some distance metric (e.g., Euclidean distance).
            2) For each data point, calculate the squared Euclidean distance between the data point and its assigned centroid.
            3) Sum up the squared distances for all data points to obtain the SSE.

        Args:
            X (array-like of shape (n_samples, n_features)):
                A list of `n_features`-dimensional data points. Each row corresponds to a single data point.
            y_pred (array-like of shape (n_samples,)): Predicted labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Sum of Squared Error Index
        """
        X = self.check_X(X)
        y_pred, _, decimal = self.get_processed_internal_data(y_pred, decimal)
        return cu.calculate_sum_squared_error_index(X, y_pred, decimal)

    def duda_hart_index(self, X=None, y_pred=None, decimal=None, **kwarg):
        """
        Computes the Duda Index or Duda-Hart index
        Smaller is better (Best = 0), Range = [0, +inf)

        Args:
            X (array-like of shape (n_samples, n_features)):
                A list of `n_features`-dimensional data points. Each row corresponds to a single data point.
            y_pred (array-like of shape (n_samples,)): Predicted labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Duda-Hart index
        """
        X = self.check_X(X)
        y_pred, _, decimal = self.get_processed_internal_data(y_pred, decimal)
        return cu.calculate_duda_hart_index(X, y_pred, decimal, self.raise_error, self.biggest_value)

    def beale_index(self, X=None, y_pred=None, decimal=None, **kwarg):
        """
        Computes the Beale Index
        Smaller is better (Best=0), Range = [0, +inf)

        Args:
            X (array-like of shape (n_samples, n_features)):
                A list of `n_features`-dimensional data points. Each row corresponds to a single data point.
            y_pred (array-like of shape (n_samples,)): Predicted labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Beale Index
        """
        X = self.check_X(X)
        y_pred, _, decimal = self.get_processed_internal_data(y_pred, decimal)
        return cu.calculate_beale_index(X, y_pred, decimal, self.raise_error, self.biggest_value)

    def r_squared_index(self, X=None, y_pred=None, decimal=None, **kwarg):
        """
        Computes the R-squared index
        Higher is better (Best=1), Range = (-inf, 1]

        Args:
            X (array-like of shape (n_samples, n_features)):
                A list of `n_features`-dimensional data points. Each row corresponds to a single data point.
            y_pred (array-like of shape (n_samples,)): Predicted labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The R-squared index
        """
        X = self.check_X(X)
        y_pred, _, decimal = self.get_processed_internal_data(y_pred, decimal)
        return cu.calculate_r_squared_index(X, y_pred, decimal)

    def density_based_clustering_validation_index(self, X=None, y_pred=None, decimal=None, **kwarg):
        """
        Computes the Density-based Clustering Validation Index
        Lower is better (Best=0), Range = [0, 1]

        Args:
            X (array-like of shape (n_samples, n_features)):
                A list of `n_features`-dimensional data points. Each row corresponds to a single data point.
            y_pred (array-like of shape (n_samples,)): Predicted labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Density-based Clustering Validation Index
        """
        X = self.check_X(X)
        y_pred, _, decimal = self.get_processed_internal_data(y_pred, decimal)
        return cu.calculate_density_based_clustering_validation_index(X, y_pred, decimal, self.raise_error, 1.0)

    def hartigan_index(self, X=None, y_pred=None, decimal=None, **kwarg):
        """
        Computes the Hartigan index for a clustering solution.
        Lower is better (best=0), Range = [0, +inf)

        Args:
            X (array-like of shape (n_samples, n_features)):
                A list of `n_features`-dimensional data points. Each row corresponds to a single data point.
            y_pred (array-like of shape (n_samples,)): Predicted labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Hartigan index
        """
        X = self.check_X(X)
        y_pred, _, decimal = self.get_processed_internal_data(y_pred, decimal)
        return cu.calculate_hartigan_index(X, y_pred, decimal)

    def baker_hubert_gamma_index(self, X=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Baker-Hubert Gamma index
        TODO: Calculate based on O(N^2) of samples --> Very slow

        Args:
            X (array-like of shape (n_samples, n_features)):
                A list of `n_features`-dimensional data points. Each row corresponds to a single data point.
            y_pred (array-like of shape (n_samples,)): Predicted labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Baker-Hubert Gamma index
        """
        X = self.check_X(X)
        y_pred, _, decimal = self.get_processed_internal_data(y_pred, decimal)
        num_samples, num_features = X.shape
        n_pairs = (num_samples * (num_samples - 1)) // 2
        distances = np.zeros(n_pairs)
        binary_vector = np.zeros(n_pairs)
        index = 0
        for idx in range(num_samples-1):
            for jdx in range(idx + 1, num_samples):
                distances[index] = np.linalg.norm(X[idx] - X[jdx])
                binary_vector[index] = 0 if y_pred[idx] == y_pred[jdx] else 1
                index += 1
        s_plus = 0
        s_minus = 0
        for idx in range(0, n_pairs-1):
            for jdx in range(idx+1, n_pairs):
                if binary_vector[idx] == 0 and binary_vector[jdx] == 1:
                    # For each within-cluster distance (B = 0), compare with between-cluster distances (B = 1).
                    s_plus += np.sum(distances[idx] < distances[jdx])
                    s_minus += np.sum(distances[idx] > distances[jdx])
        # Calculate the Gamma index
        denominator = s_plus + s_minus
        gamma_index = (s_plus - s_minus) / denominator if denominator != 0 else 0.0
        return np.round(gamma_index, decimal)

    def g_plus_index(self, X=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the G plus index
        TODO: Calculate based on O(N^2) of samples --> Very slow

        Args:
            X (array-like of shape (n_samples, n_features)):
                A list of `n_features`-dimensional data points. Each row corresponds to a single data point.
            y_pred (array-like of shape (n_samples,)): Predicted labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The G plus index
        """
        X = self.check_X(X)
        y_pred, _, decimal = self.get_processed_internal_data(y_pred, decimal)
        num_samples, num_features = X.shape
        n_pairs = (num_samples * (num_samples - 1)) // 2
        distances = np.zeros(n_pairs)
        binary_vector = np.zeros(n_pairs)
        num_discordant_pairs = 0
        for idx in range(0, n_pairs-1):
            for jdx in range(idx+1, n_pairs):
                if binary_vector[idx] == 0 and binary_vector[jdx] == 1:
                    # For each within-cluster distance (B = 0), check if it is greater than between-cluster distances (B = 1).
                    num_discordant_pairs += int(distances[idx] > distances[jdx])
        # Calculate the G plus index
        g_p = 2 * num_discordant_pairs / (n_pairs * (n_pairs - 1))
        return np.round(g_p, decimal)

    def mutual_info_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Mutual Information score between two clusterings.
        Higher is better (No best value), Range = [0, +inf)

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Mutual Information score
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        return cu.calculate_mutual_info_score(y_true, y_pred, decimal)

    def normalized_mutual_info_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the normalized mutual information between two clusterings.
        It is a variation of the mutual information score that normalizes the result to take values between 0 and 1.
        It is defined as the mutual information divided by the average entropy of the true and predicted clusterings.
        Higher is better (Best = 1), Range = [0, 1]

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The normalized mutual information score.
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        return cu.calculate_normalized_mutual_info_score(y_true, y_pred, decimal, self.raise_error, 0.0)

    def rand_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the rand score between two clusterings.
        It measures the similarity of the two sets of clusters by comparing the number
        of pairs of samples that are correctly or incorrectly clustered together.
        Higher is better (Best = 1), Range = [0, 1]

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The rand score.
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        n_samples = len(y_true)
        n_pairs = n_samples * (n_samples - 1) / 2
        a = 0  # Number of pairs that are in the same cluster in both true and predicted labels
        b = 0  # Number of pairs that are in different clusters in both true and predicted labels
        for idx in range(n_samples):
            for jdx in range(idx + 1, n_samples):
                same_cluster_true = y_true[idx] == y_true[jdx]
                same_cluster_pred = y_pred[idx] == y_pred[jdx]
                if same_cluster_true and same_cluster_pred:
                    a += 1
                elif not same_cluster_true and not same_cluster_pred:
                    b += 1
        ri = (a + b) / n_pairs
        return np.round(ri, decimal)

    def fowlkes_mallows_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Fowlkes-Mallows score between two clusterings.
        It assesses the similarity between two clustering results by comparing them to a ground truth or reference clustering (if available).
        Higher is better (Best = 1), Range = [0, 1]

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Fowlkes-Mallows score
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        n_samples = len(y_true)
        TP = 0
        FP = 0
        FN = 0
        for idx in range(n_samples):
            for jdx in range(idx + 1, n_samples):
                a = y_true[idx] == y_true[jdx]
                b = y_pred[idx] == y_pred[jdx]
                if a and b:
                    TP += 1
                elif a and not b:
                    FN += 1
                elif not a and b:
                    FP += 1
        fm = TP / np.sqrt((TP + FP) * (TP + FN))
        return np.round(fm, decimal)

    def homogeneity_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Homogeneity Score between two clusterings.
        Higher is better (Best = 1), Range = [0, 1]

        It measures the extent to which each cluster contains only data points that belong to a single class or category.
        In other words, homogeneity assesses whether all the data points in a cluster are members of the same true class or label.
        A higher homogeneity score indicates better clustering results, where each cluster corresponds well to a single ground truth class.

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Homogeneity Score
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        cc = cu.compute_homogeneity(y_true, y_pred)
        return np.round(cc, decimal)

    def completeness_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the completeness score between two clusterings.
        Higher is better (Best = 1), Range = [0, 1]

        It measures the ratio of samples that are correctly assigned to the same cluster to the total number of samples in the data.

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The completeness score.
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        cc = cu.compute_homogeneity(y_pred, y_true)
        return np.round(cc, decimal)

    def v_measure_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the V measure score between two clusterings.
        Higher is better (Best = 1), Range = [0, 1]

        It is a combination of two other metrics: homogeneity and completeness. Homogeneity measures whether all the
        data points in a given cluster belong to the same class. Completeness measures whether all the data points of a certain
        class are assigned to the same cluster. The V-measure combines these two metrics into a single score.

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The V measure score
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        h = cu.compute_homogeneity(y_true, y_pred)
        c = cu.compute_homogeneity(y_pred, y_true)
        if h + c == 0:
            cc = 0
        else:
            cc = 2 * (h * c) / (h + c)
        return np.round(cc, decimal)

    def precision_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Precision score between two clusterings.
        Higher is better (Best = 1), Range = [0, 1]. It is different than precision score in classification metrics

        It measures the proportion of points that are correctly grouped together in P2, given that
        they are grouped together in P1. It is calculated as the ratio of yy (the number of points that are correctly
        grouped together in both P1 and P2) to the sum of yy and ny (the number of points that are grouped together
        in P2 but not in P1). The formula for P is P = yy / (yy + ny).

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Precision score
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        yy, yn, ny, nn = cu.compute_confusion_matrix(y_true, y_pred)
        return np.round(yy / (yy + ny), decimal)

    def recall_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Recall score between two clusterings.
        Higher is better (Best = 1), Range = [0, 1]

        It measures the proportion of points that are correctly grouped together in P2, given that they are grouped
        together in P1. It is calculated as the ratio of yy to the sum of yy and yn (the number of points that
        are grouped together in P1 but not in P2). The formula for R is R = yy / (yy + yn).

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Recall score
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        yy, yn, ny, nn = cu.compute_confusion_matrix(y_true, y_pred)
        return np.round(yy / (yy + yn), decimal)

    def f_measure_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the F-Measure score between two clusterings.
        Higher is better (Best = 1), Range = [0, 1]

        It is the harmonic mean of the precision and recall coefficients, given by the formula F = 2PR / (P + R). It provides a
        single score that summarizes both precision and recall. The Fa-measure is a weighted version of the F-measure that
        allows for a trade-off between precision and recall. It is defined as Fa = (1 + a)PR / (aP + R),
        where a is a parameter that determines the relative importance of precision and recall.

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The F-Measure score
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        yy, yn, ny, nn = cu.compute_confusion_matrix(y_true, y_pred)
        p = yy / (yy + ny)
        r = yy / (yy + yn)
        return np.round(2 * p * r / (p + r), decimal)

    def czekanowski_dice_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the  Czekanowski-Dice score between two clusterings.
        It is the harmonic mean of the precision and recall coefficients. Higher is better (Best = 1), Range = [0, 1]

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Czekanowski-Dice score
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        cm = cu.compute_confusion_matrix(y_true, y_pred)
        yy, yn, ny, nn = cm
        return np.round(2 * yy / (2 * yy + yn + ny), decimal)

    def hubert_gamma_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Hubert Gamma score between two clusterings.
        Higher is better (Best = 1), Range=[-1, +1]

        The Hubert Gamma index ranges from -1 to 1, where a value of 1 indicates perfect agreement between the two partitions
        being compared, a value of 0 indicates no association between the partitions, and a value of -1 indicates
        complete disagreement between the two partitions.

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Hubert Gamma score
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        n_clusters = len(np.unique(y_pred))
        if n_clusters == 1:
            if self.raise_error:
                raise ValueError("The Hubert Gamma score is undefined when y_pred has only 1 cluster.")
            else:
                return -1.0
        cm = cu.compute_confusion_matrix(y_true, y_pred, normalize=True)
        yy, yn, ny, nn = cm
        NT = np.sum(cm)
        cc = (NT*yy - (yy+yn)*(yy+ny)) / np.sqrt((yy+yn)*(yy+ny)*(nn+yn)*(nn+ny))
        return np.round(cc, decimal)

    def jaccard_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Jaccard score between two clusterings.
        Higher is better (Best = 1), Range = [0, 1]

        It ranges from 0 to 1, where a value of 1 indicates perfect agreement between the two partitions being compared.
        A value of 0 indicates complete disagreement between the two partitions.

        The Jaccard score is similar to the Czekanowski-Dice score, but it is less sensitive to differences in cluster size. However,
        like the Czekanowski-Dice score, it may not be sensitive to certain types of differences between partitions. Therefore,
        it is often used in conjunction with other external indices to get a more complete picture of the similarity between partitions.

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Jaccard score
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        cm = cu.compute_confusion_matrix(y_true, y_pred)
        yy, yn, ny, nn = cm
        return np.round(yy / (yy + yn + ny), decimal)

    def kulczynski_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Kulczynski score between two clusterings.
        Higher is better (Best = 1), Range = [0, 1]

        It is the arithmetic mean of the precision and recall coefficients, which means that it takes into account both precision and recall.
        The Kulczynski index ranges from 0 to 1, where a value of 1 indicates perfect agreement between the two partitions
        being compared. A value of 0 indicates complete disagreement between the two partitions.

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Kulczynski score
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        cm = cu.compute_confusion_matrix(y_true, y_pred)
        yy, yn, ny, nn = cm
        cc = 0.5 * ((yy / (yy + ny)) + (yy / (yy + yn)))
        return np.round(cc, decimal)

    def mc_nemar_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Mc Nemar score between two clusterings.
        Higher is better (No best value), Range=(-inf, +inf)

        It is an adaptation of the non-parametric McNemar test for the comparison of frequencies between two paired samples.
        The McNemar index ranges from -inf to inf, where a bigger value indicates perfect agreement between the two partitions
        being compared

        Under the null hypothesis that the discordances between the partitions P1 and P2 are random, the McNemar index
        follows approximately a normal distribution. The McNemar index can be transformed into a chi-squared
        distance, which follows a chi-squared distribution with 1 degree of freedom

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Mc Nemar score
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        cm = cu.compute_confusion_matrix(y_true, y_pred)
        yy, yn, ny, nn = cm
        return np.round((nn - ny) / np.sqrt(nn + ny), decimal)

    def phi_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Phi score between two clusterings.
        Higher is better (No best value), Range = (-inf, +inf)

        It is a classical measure of the correlation between two dichotomous variables, and it can be used to measure the
        similarity between two partitions. The Phi index ranges from -inf to +inf, where a bigger value indicates perfect agreement
        between the two partitions being compared, a value of 0 indicates no association between the partitions,
        and a smaller value indicates complete disagreement between the two partitions.

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Phi score
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        n_clusters = len(np.unique(y_pred))
        if n_clusters == 1:
            if self.raise_error:
                raise ValueError("The Phi score is undefined when y_pred has only 1 cluster.")
            else:
                return self.smallest_value
        yy, yn, ny, nn = cu.compute_confusion_matrix(y_true, y_pred, normalize=True)
        numerator = yy * nn - yn * ny
        denominator = (yy + yn) * (yy + ny) * (yn + nn) * (ny + nn)
        return np.round(numerator / denominator, decimal)

    def rogers_tanimoto_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Rogers-Tanimoto score between two clusterings.
        Higher is better (Best = 1), Range = [0, 1]

        It measures the similarity between two partitions by computing the proportion of pairs of samples that are either
        in the same cluster in both partitions or in different clusters in both partitions, with an adjustment for the
        number of pairs of samples that are in different clusters in one partition but in the same cluster in the other
        partition. The Rogers-Tanimoto index ranges from 0 to 1, where a value of 1 indicates perfect agreement
        between the two partitions being compared. A value of 0 indicates complete disagreement between the two partitions.

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Rogers-Tanimoto score
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        cm = cu.compute_confusion_matrix(y_true, y_pred)
        yy, yn, ny, nn = cm
        cc = (yy + nn) / (yy + nn + 2 * (yn + ny))
        return np.round(cc, decimal)

    def russel_rao_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Russel-Rao score between two clusterings.
        Higher is better (Best = 1), Range = [0, 1]

        It measures the proportion of concordances between the two partitions by computing the proportion of pairs of samples
        that are in the same cluster in both partitions. The Russel-Rao index ranges from 0 to 1, where a value of 1 indicates
        perfect agreement between the two partitions being compared. A value of 0 indicates complete disagreement between the two partitions.

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Russel-Rao score
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        cm = cu.compute_confusion_matrix(y_true, y_pred)
        yy, yn, ny, nn = cm
        NT = np.sum(cm)
        return np.round(yy / NT, decimal)

    def sokal_sneath1_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Sokal-Sneath 1 score between two clusterings.
        Higher is better (Best = 1), Range = [0, 1]

        It measures the similarity between two partitions by computing the proportion of pairs of samples that are in the same cluster
        in both partitions, with an adjustment for the number of pairs of samples that are in different clusters in one partition
        but in the same cluster in the other partition. The Sokal-Sneath indices range from 0 to 1, where a value of 1 indicates
        perfect agreement between the two partitions being compared. A value of 0 indicates complete disagreement between the two partitions.

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Sokal-Sneath 1 score
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        cm = cu.compute_confusion_matrix(y_true, y_pred)
        yy, yn, ny, nn = cm
        cc = yy / (yy + 2 * (yn + ny))
        return np.round(cc, decimal)

    def sokal_sneath2_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Sokal-Sneath 2 score between two clusterings.
        Higher is better (Best = 1), Range = [0, 1]

        It measures the similarity between two partitions by computing the proportion of pairs of samples that are in the same cluster
        in both partitions, with an adjustment for the number of pairs of samples that are in different clusters in one partition
        but in the same cluster in the other partition. The Sokal-Sneath indices range from 0 to 1, where a value of 1 indicates
        perfect agreement between the two partitions being compared. A value of 0 indicates complete disagreement between the two partitions.

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Sokal-Sneath 2 score
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        cm = cu.compute_confusion_matrix(y_true, y_pred)
        yy, yn, ny, nn = cm
        cc = (yy + nn) / (yy + nn + 0.5 * (yn + ny))
        return np.round(cc, decimal)

    def purity_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Purity score
        Higher is better (Best = 1), Range = [0, 1]

        Purity is a metric used to evaluate the quality of clustering results, particularly in situations where the
        ground truth labels of the data points are known. It measures the extent to which the clusters produced by
        a clustering algorithm match the true class labels of the data.

        Here's how Purity is calculated:
            1) For each cluster, find the majority class label among the data points in that cluster.
            2) Sum up the sizes of the clusters that belong to the majority class label.
            3) Divide the sum by the total number of data points.

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Purity score
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        # Find the number of data points
        N = len(y_true)
        # Find the unique class labels in the true labels
        unique_classes = np.unique(y_true)
        # Initialize the purity score
        purity = 0
        # Iterate over each unique class label
        for c in unique_classes:
            # Find the indices of data points with the current class label in the true labels
            class_indices = np.where(y_true == c)[0]
            # Find the corresponding predicted labels for these data points
            class_predictions = y_pred[class_indices]
            # Count the occurrences of each predicted label
            class_counts = np.bincount(class_predictions)
            # Add the size of the majority class to the purity score
            purity += np.max(class_counts)
        # Normalize the purity score by dividing by the total number of data points
        return np.round(purity/N, decimal)

    def entropy_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Entropy score
        Smaller is better (Best = 0), Range = [0, 1]

        Entropy is a metric used to evaluate the quality of clustering results, particularly when the ground truth labels of the
        data points are known. It measures the amount of uncertainty or disorder within the clusters produced by a clustering algorithm.

        Here's how the Entropy score is calculated:

            1) For each cluster, compute the class distribution by counting the occurrences of each class label within the cluster.
            2) Normalize the class distribution by dividing the count of each class label by the total number of data points in the cluster.
            3) Compute the entropy for each cluster using the normalized class distribution.
            4) Weight the entropy of each cluster by its relative size (proportion of data points in the whole dataset).
            5) Sum up the weighted entropies of all clusters.

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Entropy score
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        # Find the number of data points
        N = len(y_true)
        # Find the unique class labels in the true labels
        unique_classes = np.unique(y_true)
        result = 0
        # Iterate over each unique class label
        for c in unique_classes:
            # Find the indices of data points with the current class label in the true labels
            class_indices = np.where(y_true == c)[0]
            # Find the corresponding predicted labels for these data points
            class_predictions = y_pred[class_indices]
            # Count the occurrences of each predicted label
            class_counts = np.bincount(class_predictions)
            # Normalize the class counts by dividing by the total number of data points in the cluster
            class_distribution = class_counts / len(class_predictions)
            # Compute the entropy of the cluster
            cluster_entropy = cu.calculate_entropy(class_distribution, base=2)
            # Weight the entropy by the relative size of the cluster
            cluster_size = len(class_indices)
            result += (cluster_size / N) * cluster_entropy
        return np.round(result, decimal)

    def tau_score(self, y_true=None, y_pred=None, decimal=None, **kwargs):
        """
        Computes the Tau Score between two clustering solutions.
        Higher is better (Best = 1), Range = [-1, 1]

        The Tau score, also known as the Tau coefficient, is a measure of agreement or similarity between two clustering solutions.
        It is commonly used to compare the similarity of two different clusterings or to evaluate the stability of a clustering algorithm.

        Args:
            y_true (array-like): The true labels for each sample.
            y_pred (array-like): The predicted cluster labels for each sample.
            decimal (int): The number of fractional parts after the decimal point

        Returns:
            result (float): The Tau Score
        """
        y_true, y_pred, _, decimal = self.get_processed_external_data(y_true, y_pred, decimal)
        n = len(y_true)
        concordant_pairs = 0
        discordant_pairs = 0
        for idx in range(n):
            for jdx in range(idx + 1, n):
                if y_true[idx] == y_true[jdx] and y_pred[idx] == y_pred[jdx]:
                    concordant_pairs += 1
                elif y_true[idx] != y_true[jdx] and y_pred[idx] != y_pred[jdx]:
                    concordant_pairs += 1
                else:
                    discordant_pairs += 1
        result = (concordant_pairs - discordant_pairs) / (concordant_pairs + discordant_pairs)
        return np.round(result, decimal)

    BHI = ball_hall_index
    XBI = xie_beni_index
    DBI = davies_bouldin_index
    BRI = banfeld_raftery_index
    KDI = ksq_detw_index
    DRI = det_ratio_index
    DI = dunn_index
    CHI = calinski_harabasz_index
    LDRI = log_det_ratio_index
    LSRI = log_ss_ratio_index
    SI = silhouette_index
    SSEI = sum_squared_error_index
    DHI = duda_hart_index
    BI = beale_index
    RSI = r_squared_index
    DBCVI = density_based_clustering_validation_index
    HI = hartigan_index

    BHGI = baker_hubert_gamma_index
    GPI = g_plus_index

    MIS = mutual_info_score
    NMIS = normalized_mutual_info_score
    RaS = rand_score
    FMS = fowlkes_mallows_score
    HS = homogeneity_score
    CS = completeness_score
    VMS = v_measure_score
    PrS = precision_score
    ReS = recall_score
    FmS = f_measure_score
    CDS = czekanowski_dice_score
    HGS = hubert_gamma_score
    JS = jaccard_score
    KS = kulczynski_score
    MNS = mc_nemar_score
    PhS = phi_score
    RTS = rogers_tanimoto_score
    RRS = russel_rao_score
    SS1S = sokal_sneath1_score
    SS2S = sokal_sneath2_score
    PuS = purity_score
    ES = entropy_score
    TS = tau_score
