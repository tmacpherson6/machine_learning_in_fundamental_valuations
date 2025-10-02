"""This module contains helper functions for the unsupervised learning section."""
from helpers import get_quarters

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

# Sci-kit Learn Functions
from sklearn.preprocessing import StandardScaler, RobustScaler, QuantileTransformer
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.manifold import MDS, TSNE


def get_KPI(input_df: pd.DataFrame) -> pd.DataFrame:
    """Selects the KPIs from the data."""
    cols_to_keep = []
    for column in input_df.columns:
        if 'KPI' in column:
            if 'QoQ' not in column:
                cols_to_keep.append(column)
    return input_df[cols_to_keep].copy()


def get_Rate(input_df: pd.DataFrame, include_KPI_rate=False) -> pd.DataFrame:
    """Selects the QoQ and other Rate features from the data."""
    cols_to_keep = []
    for column in input_df.columns:
        if ('Rate' in column) or ('QoQ' in column):
            if include_KPI_rate:
                cols_to_keep.append(column)
            else:
                if 'KPI' not in column:
                    cols_to_keep.append(column)
    return input_df[cols_to_keep].copy()


def get_Macro(input_df: pd.DataFrame) -> pd.DataFrame:
    """Selects the macroeconomic variables from the data."""
    macro_vars=['GDP_',
                'GDPReal_',
                'Unemployment',
                'Ineterest',
                'Industrial',
                'Inflation'
               ]
    cols_to_keep = []
    for column in input_df.columns:
        for var in macro_vars:
            if var in column:
                cols_to_keep.append(column)
    return input_df[cols_to_keep].copy()


def process_for_PCA(input_df: pd.DataFrame, 
                    log_transform=False, 
                    drop_base_data=False,
                    scaler='quantile',
                    verbose=False
                   ) -> pd.DataFrame:
    """Processes a dataframe before applying PCA."""
    # Include only numeric columns
    if verbose:
        print('Dropping non-numeric columns.')
    dataset = input_df.select_dtypes(include='number').copy()
    if verbose:
        print(f'Remaining dtypes: {dataset.dtypes.unique()}')
    if log_transform:
        quarters = get_quarters(dataset)
        log_vars = ['CurrentAssets',
                    'CurrentLiabilities',
                    'TotalAssets',
                    'TotalLiabilities',
                    'TotalDebt'
                   ]
        for var in log_vars:
            for quarter in quarters:
                dataset['log2_' + var + quarter] = (
                    dataset[var + quarter] + 2
                ).apply(np.log2).copy()
    if drop_base_data:
        base_data = []
        for column in dataset.select_dtypes(include=['float64']).columns:
            if 'QoQ' not in column:
                if 'KPI' not in column:
                    if 'GDP' not in column:
                        if 'Unemployment' not in column:
                            if 'Rate' not in column:
                                if 'Industrial' not in column:
                                    if 'Inflation' not in column:
                                        if 'log2_' not in column:
                                            base_data.append(column)
        if verbose:
            print('\nDropping raw company financial data:')
            for column in base_data:
                print(column)
        dataset.drop(columns=base_data, inplace=True)
    if verbose:
        print(f'There are {dataset.shape[0]} rows and {dataset.shape[1]} columns in the dataset.')
    if scaler == 'robust':
        scaler = RobustScaler()
    elif scaler == 'quantile':
        scaler = QuantileTransformer(output_distribution='normal')
    else:
        scaler = StandardScaler()
    return pd.DataFrame(scaler.fit_transform(dataset))


def elbow_plot(
    data: np.ndarray,
    title='Elbow Plot',
    xlabel='Score',
    ylabel='Number'
):
    """Creates an elbow plot from a set of coordinates (data).

    Keyword Arguments:
    data -- ndarray of coordinates (x, y) to plot
    title -- title for the plot
    xlabel -- label for the x-axis
    ylabel -- label for the y-axis
    """
    fig = plt.figure(figsize=(4, 3))
    ax = fig.subplots()
    ax.plot(data[:, 0], data[:, 1])
    ax.set_title(title)
    ax.set_ylabel(xlabel)
    ax.set_xlabel(ylabel)
    fig.tight_layout()
    plt.show()
    return None


def plot_cum_variance_explained(
    explained_variance_ratio: list,
    *,
    subset=None,
    n=None
):
    """Plots cumulative variance explained by top n Principal Components."""
    if n is None:
        n = len(explained_variance_ratio)
    fig = plt.figure(figsize=(4, 3))
    ax = fig.subplots()
    ax.plot(
        range(n),
        np.cumsum(explained_variance_ratio[:n]),
        alpha=0.75
    )
    ax.set_title('Cumulative Variance Explained')
    ax.set_xlabel('Number of Principal Components')
    ax.set_ylabel('Fraction of Variance Explained')
    if subset is not None:
        cum_var = [np.sum(explained_variance_ratio[:i]) for i in subset]
        ax.bar(subset, cum_var, width=0.5, alpha=0.75)
        for i in range(len(subset)):
            ax.text(subset[i], 
                    cum_var[i] +0.025,
                    str(int(cum_var[i] * 100)) + '%',
                    horizontalalignment='center',
                    verticalalignment='bottom',
                   )
    fig.tight_layout()
    plt.show()
    return None


def biplot(score, coeff):
    """Displays a biplot for PCA data.
    
    Original Author: Serafeim Loukas, serafeim.loukas@epfl.ch
    Modified by: Peter King, kingpete@umich.edu
    Inputs:
       score: the projected data
       coeff: the eigenvectors (PCs)
    """
    xs = score[:, 0] / 400 # projection on PC1
    ys = score[:, 1] / 160 # projection on PC2
    n = coeff.shape[0] # number of variables
    plt.figure(figsize=(10, 8), dpi=100)
    for i in range(n):
        plt.arrow(0, 0, coeff[i, 0], coeff[i, 1], 
                  color='k', alpha=0.9, linestyle='-', linewidth=1.5, overhang=0.2
                 )
    plt.xlabel("PC{}".format(1), size=14)
    plt.ylabel("PC{}".format(2), size=14)
    limx = int(xs.max()) + 1
    limy = int(ys.max()) + 1
    plt.xlim([-limx, limx])
    plt.ylim([-limy, limy])
    plt.grid()
    plt.tick_params(axis='both', which='both', labelsize=14)
    plt.show()
    return None
    

def get_wgss(data: np.ndarray, max_clusters=10) -> dict:
    """Calculates WGSS for a range of clusters using K-Means.

    Keyword Arguments:
    data -- numpy array of PCA-transformed data
    max_clusters -- maximum number of clusters to try
    """
    wgss = {}
    for n_clusters in tqdm(range(1, max_clusters + 1)):
        kmeans = KMeans(n_clusters, init='random', n_init=100, copy_x=False)
        kmeans.fit(data)
        # Record within-group sum of squares (WGSS)
        # WGSS is the sum of squared distance from each data point in a cluster
        # to the cluster mean (centroid); Lower WGSS indicates "better clustering"
        wgss[n_clusters] = kmeans.inertia_
    return wgss
