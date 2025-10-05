'''
Pipeline File 4

This part of our pipeline is going to separate the data into a training and a
testing set. We want to do this early, before all imputation and transformations so that there is no risk of data leakage.

We will be stratifying our split based on market capitalization per sector to ensure that both the training and testing sets have a representative distribution of companies across different market cap sizes and sectors.
'''

import argparse
import pandas as pd
from typing import List, Tuple
from sklearn.model_selection import train_test_split
from data_acquisition import save_to_csv


def get_X_y_columns(dataset: pd.DataFrame, target_string: str) -> Tuple[List[str],List[str]]:
    '''
    We want to identify the columns that will be used as features (X) and the target variable (y).
    '''
    y_columns = []
    X_columns = []
    columns = dataset.columns
    for column in columns:
        if target_string in column:
            y_columns.append(column)
        else:
            X_columns.append(column)
    #y_cols.append('Ticker')
    
    return X_columns, y_columns


def create_strata(dataset: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    '''
    Create strata based on Market Cap and Sector.
    '''
    strat = dataset['Market Cap'].astype(str) + "_" + dataset['Sector'].astype(str)
    val_cou = strat.value_counts()
    to_strat = strat.isin(val_cou[val_cou >= 2].index)
    # Now, let's pull out those
    dataset, strat = dataset.loc[to_strat],strat.loc[to_strat]
    return dataset, strat


def split_data(dataset: pd.DataFrame, X_columns: List[str], y_columns: List[str], strat: pd.Series, test_size: float = 0.2, random_state: int = 6) -> Tuple[pd.DataFrame,pd.DataFrame,pd.DataFrame,pd.DataFrame]:
    '''
    Split the data into training and testing sets using stratified sampling.
    '''
    idx_tr, idx_te = train_test_split(dataset.index, test_size = test_size, random_state = random_state, stratify = strat)
    
    X_tr = dataset.loc[idx_tr,X_columns]
    y_tr = dataset.loc[idx_tr,y_columns]
    X_te = dataset.loc[idx_te,X_columns]
    y_te = dataset.loc[idx_te,y_columns]
    
    return X_tr,X_te,y_tr,y_te


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input_file', help='name of input file: Russell_3000_Cleaned.csv'
    )
    parser.add_argument('target_string', help='y_target column string example: _2025Q2')
    args = parser.parse_args()
    
    # Load input file, clean dataframe, and write output file
    df = pd.read_csv(args.input_file)
    df.set_index('Ticker',inplace=True)

    # Identify the columns
    X_columns, y_columns = get_X_y_columns(df, args.target_string)

    # Get the dataset and startification series
    dataset, strat = create_strata(df)
    
    # Split the data
    X_tr, X_te, y_tr, y_te = split_data(dataset, X_columns, y_columns, strat)
    #print(y_tr.head())
    
    # Save the data
    save_to_csv(X_tr, "X_train.csv", index=True)
    save_to_csv(y_tr, "y_train.csv", index=True)
    save_to_csv(X_te, "X_test.csv", index=True)
    save_to_csv(y_te, "y_test.csv", index=True)

    print("Saved Training and Testing Data Files")