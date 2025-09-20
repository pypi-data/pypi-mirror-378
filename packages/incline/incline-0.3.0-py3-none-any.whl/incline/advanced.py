"""
Advanced trend estimation methods for incline package.

This module provides more sophisticated trend estimation techniques beyond
the basic Savitzky-Golay and spline methods, including local polynomial
regression, trend filtering, and state-space models.
"""

import numpy as np
import pandas as pd
from typing import Optional, Union, Tuple, Literal
import warnings

# Check for optional dependencies
try:
    from statsmodels.nonparametric.smoothers_lowess import lowess
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False

try:
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import PolynomialFeatures
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

from .trend import compute_time_deltas


def loess_trend(
    df: pd.DataFrame,
    column_value: str = 'value',
    time_column: Optional[str] = None,
    frac: float = 0.3,
    derivative_order: int = 1,
    degree: int = 1,
    robust: bool = True
) -> pd.DataFrame:
    """
    Estimate trend using LOESS (locally weighted scatterplot smoothing).

    LOESS fits local polynomial regressions to estimate the derivative at each point.
    This is the canonical nonparametric derivative estimator with good statistical
    properties.

    Parameters
    ----------
    df : pd.DataFrame
        Time series data
    column_value : str
        Column name containing the values
    time_column : str, optional
        Column name for time values (if None, uses index)
    frac : float
        Fraction of data to use for each local regression (bandwidth)
    derivative_order : int
        Order of derivative (1 for slope, 2 for acceleration)
    degree : int
        Degree of local polynomial (1=linear, 2=quadratic)
    robust : bool
        Use robust fitting to downweight outliers

    Returns
    -------
    pd.DataFrame
        Original data plus smoothed values and derivatives

    Notes
    -----
    This function wraps statsmodels LOWESS and estimates derivatives by
    fitting local polynomials in a sliding window around each point.
    The derivative is extracted from the polynomial coefficients.
    """
    if not HAS_STATSMODELS:
        raise ImportError(
            "statsmodels is required for LOESS trend estimation. "
            "Install with: pip install statsmodels"
        )

    y = df[column_value].values

    # Get time values
    if time_column:
        x = df[time_column].values
    elif isinstance(df.index, pd.DatetimeIndex):
        x, delta = compute_time_deltas(df.index)
    else:
        x = np.arange(len(df), dtype=float)

    # Apply LOWESS for smoothing
    smoothed_result = lowess(
        y, x,
        frac=frac,
        it=3 if robust else 0,  # iterations for robust fitting
        delta=0.0,  # no delta approximation
        return_sorted=False
    )

    smoothed_values = smoothed_result

    # Estimate derivatives using local polynomial fits
    n = len(x)
    derivatives = np.zeros(n)

    # Calculate window size from frac
    window_size = max(3, int(frac * n))
    if window_size % 2 == 0:
        window_size += 1
    half_window = window_size // 2

    for i in range(n):
        # Define local window
        start_idx = max(0, i - half_window)
        end_idx = min(n, i + half_window + 1)

        # Get local data
        x_local = x[start_idx:end_idx]
        y_local = smoothed_values[start_idx:end_idx]

        if len(x_local) < degree + 1:
            derivatives[i] = np.nan
            continue

        # Fit local polynomial
        try:
            # Center x around current point for numerical stability
            x_centered = x_local - x[i]
            coeffs = np.polyfit(x_centered, y_local, degree)

            # Extract derivative from polynomial coefficients
            if derivative_order == 1 and len(coeffs) >= 2:
                # First derivative coefficient
                derivatives[i] = coeffs[-2]
            elif derivative_order == 2 and len(coeffs) >= 3:
                # Second derivative coefficient (times 2)
                derivatives[i] = 2 * coeffs[-3]
            else:
                derivatives[i] = np.nan

        except (np.linalg.LinAlgError, np.RankWarning):
            derivatives[i] = np.nan

    # Create output dataframe
    odf = df.copy()
    odf['smoothed_value'] = smoothed_values
    odf['derivative_value'] = derivatives
    odf['function_order'] = degree
    odf['derivative_method'] = 'loess'
    odf['derivative_order'] = derivative_order
    odf['bandwidth'] = frac
    odf['robust'] = robust

    return odf


def l1_trend_filter(
    df: pd.DataFrame,
    column_value: str = 'value',
    time_column: Optional[str] = None,
    lambda_param: float = 1.0,
    derivative_order: int = 1,
    max_iter: int = 100,
    tol: float = 1e-4
) -> pd.DataFrame:
    """
    Estimate trend using L1 trend filtering (fused lasso).

    L1 trend filtering fits piecewise polynomial trends by penalizing
    discrete differences. This produces sparse changepoints and is
    robust to outliers.

    Parameters
    ----------
    df : pd.DataFrame
        Time series data
    column_value : str
        Column name containing the values
    time_column : str, optional
        Column name for time values
    lambda_param : float
        Regularization parameter (larger = smoother)
    derivative_order : int
        Order of trend filtering (1=piecewise linear, 2=piecewise quadratic)
    max_iter : int
        Maximum iterations for optimization
    tol : float
        Convergence tolerance

    Returns
    -------
    pd.DataFrame
        Original data plus trend estimates and changepoints

    Notes
    -----
    This implements the L1 trend filtering algorithm using ADMM.
    The result is a piecewise polynomial trend with sparse changes.
    """
    y = df[column_value].values
    n = len(y)

    # Get time values (for proper scaling)
    if time_column:
        x = df[time_column].values
        delta = np.median(np.diff(x))
    elif isinstance(df.index, pd.DatetimeIndex):
        x, delta = compute_time_deltas(df.index)
    else:
        x = np.arange(n, dtype=float)
        delta = 1.0

    # Create difference matrix
    if derivative_order == 1:
        # First-order differences (piecewise linear)
        D = np.diff(np.eye(n), axis=0)
    elif derivative_order == 2:
        # Second-order differences (piecewise quadratic)
        D = np.diff(np.eye(n), n=2, axis=0)
    else:
        raise ValueError("derivative_order must be 1 or 2")

    # Scale by time step
    D = D / (delta ** derivative_order)

    # Solve L1 trend filtering using ADMM
    # min_x (1/2)||y - x||_2^2 + lambda||Dx||_1

    # ADMM variables
    x_trend = y.copy()  # primal variable
    z = np.zeros(D.shape[0])  # auxiliary variable
    u = np.zeros(D.shape[0])  # dual variable

    rho = 1.0  # ADMM penalty parameter

    # Precompute matrices for efficiency
    DTD = D.T @ D
    I = np.eye(n)
    A_inv = np.linalg.inv(I + rho * DTD)

    for iteration in range(max_iter):
        x_old = x_trend.copy()

        # x-update (quadratic)
        x_trend = A_inv @ (y + rho * D.T @ (z - u))

        # z-update (soft thresholding)
        Dx_plus_u = D @ x_trend + u
        z = soft_threshold(Dx_plus_u, lambda_param / rho)

        # u-update (dual)
        u = u + D @ x_trend - z

        # Check convergence
        if np.linalg.norm(x_trend - x_old) < tol:
            break

    # Compute derivatives from trend
    if derivative_order == 1:
        derivatives = np.diff(x_trend) / delta
        # Extend to original length
        derivatives = np.concatenate([derivatives, [derivatives[-1]]])
    else:
        derivatives = np.diff(x_trend, n=2) / (delta ** 2)
        # Extend to original length
        derivatives = np.concatenate([[derivatives[0]], derivatives, [derivatives[-1]]])

    # Detect changepoints (where derivative changes significantly)
    if derivative_order == 1:
        changes = np.abs(np.diff(derivatives)) > 0.1 * np.std(derivatives)
        changepoints = np.zeros(n, dtype=bool)
        if len(changes) > 0:
            changepoints[1:1+len(changes)] = changes
    else:
        changes = np.abs(derivatives) > 0.1 * np.std(derivatives)
        changepoints = changes

    # Create output dataframe
    odf = df.copy()
    odf['smoothed_value'] = x_trend
    odf['derivative_value'] = derivatives
    odf['function_order'] = derivative_order
    odf['derivative_method'] = 'l1_filter'
    odf['derivative_order'] = derivative_order
    odf['lambda'] = lambda_param
    odf['changepoint'] = changepoints

    return odf


def soft_threshold(x: np.ndarray, threshold: float) -> np.ndarray:
    """Soft thresholding operator for L1 regularization."""
    return np.sign(x) * np.maximum(np.abs(x) - threshold, 0)


def local_polynomial_trend(
    df: pd.DataFrame,
    column_value: str = 'value',
    time_column: Optional[str] = None,
    bandwidth: float = 0.2,
    degree: int = 1,
    kernel: str = 'gaussian',
    derivative_order: int = 1
) -> pd.DataFrame:
    """
    Local polynomial trend estimation with kernel weighting.

    This implements the Fan-Gijbels local polynomial estimator, which is
    the theoretical foundation for nonparametric derivative estimation.

    Parameters
    ----------
    df : pd.DataFrame
        Time series data
    column_value : str
        Column name containing values
    time_column : str, optional
        Time column name
    bandwidth : float
        Bandwidth parameter (fraction of data range)
    degree : int
        Polynomial degree for local fits
    kernel : str
        Kernel function ('gaussian', 'epanechnikov', 'uniform')
    derivative_order : int
        Order of derivative to estimate

    Returns
    -------
    pd.DataFrame
        Results with smoothed values and derivatives
    """
    if not HAS_SKLEARN:
        raise ImportError(
            "scikit-learn is required for local polynomial estimation. "
            "Install with: pip install scikit-learn"
        )

    y = df[column_value].values
    n = len(y)

    # Get time values
    if time_column:
        x = df[time_column].values
    elif isinstance(df.index, pd.DatetimeIndex):
        x, delta = compute_time_deltas(df.index)
    else:
        x = np.arange(n, dtype=float)

    # Calculate bandwidth in data units
    x_range = np.ptp(x)
    h = bandwidth * x_range

    smoothed_values = np.zeros(n)
    derivatives = np.zeros(n)

    # Kernel function
    def kernel_weight(distances, kernel_type):
        """Compute kernel weights for given distances."""
        u = distances / h

        if kernel_type == 'gaussian':
            return np.exp(-0.5 * u**2)
        elif kernel_type == 'epanechnikov':
            return np.maximum(0, 0.75 * (1 - u**2))
        elif kernel_type == 'uniform':
            return (np.abs(u) <= 1).astype(float)
        else:
            raise ValueError(f"Unknown kernel: {kernel_type}")

    # Fit local polynomial at each point
    for i in range(n):
        x_center = x[i]

        # Compute distances and weights
        distances = np.abs(x - x_center)
        weights = kernel_weight(distances, kernel)

        # Only use points with non-zero weights
        mask = weights > 1e-10
        if np.sum(mask) < degree + 1:
            smoothed_values[i] = y[i]
            derivatives[i] = np.nan
            continue

        x_local = x[mask] - x_center  # Center around evaluation point
        y_local = y[mask]
        w_local = weights[mask]

        # Create polynomial features
        poly = PolynomialFeatures(degree=degree, include_bias=True)
        X_local = poly.fit_transform(x_local.reshape(-1, 1))

        # Weighted least squares
        try:
            # Manual weighted least squares
            W = np.diag(w_local)
            XTW = X_local.T @ W
            coeffs = np.linalg.solve(XTW @ X_local, XTW @ y_local)

            # Evaluate at center point (x_local = 0)
            smoothed_values[i] = coeffs[0]  # constant term

            # Extract derivative
            if derivative_order == 1 and len(coeffs) >= 2:
                derivatives[i] = coeffs[1]  # linear coefficient
            elif derivative_order == 2 and len(coeffs) >= 3:
                derivatives[i] = 2 * coeffs[2]  # quadratic coefficient * 2
            else:
                derivatives[i] = np.nan

        except np.linalg.LinAlgError:
            smoothed_values[i] = y[i]
            derivatives[i] = np.nan

    # Create output dataframe
    odf = df.copy()
    odf['smoothed_value'] = smoothed_values
    odf['derivative_value'] = derivatives
    odf['function_order'] = degree
    odf['derivative_method'] = 'local_poly'
    odf['derivative_order'] = derivative_order
    odf['bandwidth'] = bandwidth
    odf['kernel'] = kernel

    return odf


# Selection function for automatic method choice
def select_trend_method(
    df: pd.DataFrame,
    column_value: str = 'value',
    time_column: Optional[str] = None,
    criteria: str = 'auto'
) -> str:
    """
    Automatically select the best trend estimation method for the data.

    Parameters
    ----------
    df : pd.DataFrame
        Time series data
    column_value : str
        Value column name
    time_column : str, optional
        Time column name
    criteria : str
        Selection criteria ('auto', 'robust', 'smooth', 'changepoints')

    Returns
    -------
    str
        Recommended method name
    """
    n = len(df)
    y = df[column_value].values

    # Get time regularity
    if time_column:
        x = df[time_column].values
        time_regular = np.std(np.diff(x)) / np.mean(np.diff(x)) < 0.05
    elif isinstance(df.index, pd.DatetimeIndex):
        x, _ = compute_time_deltas(df.index)
        time_regular = np.std(np.diff(x)) / np.mean(np.diff(x)) < 0.05
    else:
        time_regular = True

    # Estimate noise level and trend strength
    noise_level = np.std(np.diff(y, n=2))  # second differences
    trend_strength = np.std(np.diff(y))    # first differences
    signal_to_noise = trend_strength / (noise_level + 1e-10)

    # Check for outliers
    q75, q25 = np.percentile(y, [75, 25])
    iqr = q75 - q25
    outlier_fraction = np.mean(
        (y < q25 - 1.5 * iqr) | (y > q75 + 1.5 * iqr)
    )

    if criteria == 'auto':
        if outlier_fraction > 0.1:
            return 'loess'  # Robust to outliers
        elif signal_to_noise < 2:
            return 'spline'  # Good for noisy data
        elif not time_regular:
            return 'local_poly'  # Handles irregular sampling
        elif n < 50:
            return 'sgolay'  # Simple for small datasets
        else:
            return 'loess'  # Generally robust choice

    elif criteria == 'robust':
        return 'loess' if HAS_STATSMODELS else 'l1_filter'

    elif criteria == 'smooth':
        return 'spline'

    elif criteria == 'changepoints':
        return 'l1_filter'

    else:
        raise ValueError(f"Unknown criteria: {criteria}")


# Unified interface function
def estimate_trend(
    df: pd.DataFrame,
    column_value: str = 'value',
    time_column: Optional[str] = None,
    method: str = 'auto',
    **kwargs
) -> pd.DataFrame:
    """
    Unified interface for trend estimation with automatic method selection.

    Parameters
    ----------
    df : pd.DataFrame
        Time series data
    column_value : str
        Value column name
    time_column : str, optional
        Time column name
    method : str
        Method to use ('auto', 'loess', 'l1_filter', 'local_poly', 'spline', 'sgolay')
    **kwargs
        Method-specific parameters

    Returns
    -------
    pd.DataFrame
        Results with trend estimates and derivatives
    """
    if method == 'auto':
        method = select_trend_method(df, column_value, time_column)

    if method == 'loess':
        return loess_trend(df, column_value, time_column, **kwargs)
    elif method == 'l1_filter':
        return l1_trend_filter(df, column_value, time_column, **kwargs)
    elif method == 'local_poly':
        return local_polynomial_trend(df, column_value, time_column, **kwargs)
    elif method == 'spline':
        from .trend import spline_trend
        return spline_trend(df, column_value, time_column, **kwargs)
    elif method == 'sgolay':
        from .trend import sgolay_trend
        return sgolay_trend(df, column_value, time_column, **kwargs)
    else:
        raise ValueError(f"Unknown method: {method}")
