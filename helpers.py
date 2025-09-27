"""This module contains helper functions for the Milestone II Project."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def get_quarters(input_df: pd.DataFrame) -> list:
    """Get a list of quarters in the data."""
    quarters = set()
    for column in input_df.columns:
        if column[-2] == 'Q':
            if column[-7] == '_':
                quarters.add(column[-7:])
    # Drop 2024Q1 if needed:
    if 'Revenue_2024Q1' not in input_df.columns:
        quarters.discard('_2024Q1')
    quarters = sorted(list(quarters))
    return quarters


def string_to_float(input_Series: pd.Series) -> pd.Series:
    """Converts a 'numeric' Series of dtype string to dtype float.
    
    Keyword Arguments:
    input_Series -- a pandas Series to be converted from str to float
    """
    return input_Series.apply(str.replace, args=(',', '')).astype(np.float64)


def log_transform(input_df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Applies a log transformation to selected base variables in the data."""
    dataset = input_df.copy()
    for column in columns:
        dataset['log_' + column] = dataset[column].apply(np.log)
    return dataset


def plot_residuals(X, y):
    """Plots the residuals for a univariate OLS regression."""
    # Run univariate OLS regression
    model = sm.OLS(y, sm.add_constant(X))
    results = model.fit()
    # Plot residual distribution vs. the covariate
    fig = plt.figure()
    ax = fig.subplots()
    ax.scatter(X, results.resid)
    plt.title('Residuals of ' + X.name)
    plt.show()
    # Show a QQ-plot for residuals
    sm.qqplot(results.resid, line='s')
    plt.title('QQ-Plot of residuals for ' + X.name)
    plt.show()

