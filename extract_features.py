"""Augments a dataframe with PCA-extracted features and K-Means cluster labels.

This module is intended to augment the X_train and X_test dataframes with additional 
features derived from PCA extraction and K-Means clustering techniques.

Additionally, it preserves all objects as python 'pickle' files so that results can be replicated in the future.
"""
import argparse

from helpers import *
from unsupervised_helpers import *


def extract_features(input_df: pd.DataFrame, pickle_path='pickles/') -> pd.DataFrame:
    """Extract features from a training dataset using PCA.

    Use this function only on the TRAINING set.
    This function extracts features using PCA and assigns cluster labels
    using K-Means.  It also saves an augmented dataframe as a CSV file, and 
    preserves the objects used to transform the data as 'pickle' files.
    """
    dataset = input_df.copy()
    if 'Unnamed: 0' in dataset.columns:
        dataset.drop(columns=['Unnamed: 0'], inplace=True)
    # Process for PCA
    pca_df = process_for_PCA(dataset)
    # We found that the top 50 PCs explain 85% of the variance
    pca = PCA(50)
    X_PCA = pca.fit_transform(pca_df)
    # Pickle the pca object
    with open(pickle_path + 'pca_all.pickle', 'wb') as f:
        pickle.dump(pca, f)
    # Make a dataframe of the top 50 PCs
    PCA_cols = ['PCA_all_PC' + str(i + 1) for i in range(X_PCA.shape[1])]
    top50_PC_all_df = pd.DataFrame(X_PCA, columns=PCA_cols)
    # Perform PCA using only the KPI subset
    subset_df = get_KPI(dataset)
    subset_pca_df = process_for_PCA(subset_df)
    pca_KPI = PCA(10)
    X_PCA_KPI = pca_KPI.fit_transform(pca_df)
    # pickle the pca_KPI object
    with open(pickle_path + 'pca_KPI.pickle', 'wb') as f:
        pickle.dump(pca_KPI, f)
    # Make a dataframe of the top 10 PCs from the KPI subset
    PCA_KPI_cols = ['PCA_KPI_PC' + str(i + 1) for i in range(X_PCA_KPI.shape[1])]
    top10_PC_KPI_df = pd.DataFrame(X_PCA_KPI, columns=PCA_KPI_cols)
    # Use K-Means to assign cluster labels
    kmeans = KMeans(n_clusters=7, init='random', n_init=100, copy_x=False)
    cluster = kmeans.fit_predict(X_PCA_KPI)
    # Pickle the K-Means object
    with open(pickle_path + 'kmeans.pickle', 'wb') as f:
        pickle.dump(kmeans, f)
    # Create augmented DataFrame
    augmented_df = pd.concat(
        (
            dataset,
            top50_PC_all_df,
            top10_PC_KPI_df,
            pd.Series(cluster, name='Cluster')
        ), axis = 1
    )
    return augmented_df
    

if __name__ == '__main__':
    # Get command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input_file', help='name of input file: X_train_filled_KPIs_QoQ.csv'
    )
    parser.add_argument(
        'output_file', help='name of output file: X_train_filled_KPIs_QoQ_PCA.csv'
    )
    args = parser.parse_args()
    # Load input file, clean dataframe, and write output file
    df = pd.read_csv(args.input_file)
    augmented_df = extract_features(df)
    augmented_df.to_csv(args.output_file, index=False)
    print(f"Augmented DataFrame saved to {args.output_file}")