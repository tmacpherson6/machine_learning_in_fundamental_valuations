"""Clean company financial and macro data.

Command Line usage (example for Linux):
 python clean.py <in_file.csv> <out_file.csv>
Arguments:
 <in_file.csv> -- the CSV file to be cleaned by this module
 <out_file.csv> -- the cleaned CSV file to write to disk
"""
import argparse

import numpy as np
import pandas as pd


def clean(input_df: pd.DataFrame) -> pd.DataFrame:
    """Cleans the dataframe.
    
    This function is not very modular.  It uses column names that are
    specific to the Russell_3000 data. 
    """
    dataset = input_df.copy()
    # Drop duplicates
    dataset.drop_duplicates(inplace=True)
    # Drop where ticker is duplicated
    duplicates = dataset.loc[(
        dataset.duplicated('Ticker', keep=False)
    )].sort_values('Ticker')
    dataset.drop(index=list(duplicates.index), inplace=True)
    # Keep only one Ticker column
    dataset.drop(columns=['OriginalTicker', 'YahooSymbol'], inplace=True)
    # Keep only entries that are classified as Equity
    dataset = dataset[dataset['Asset Class'] == 'Equity'].copy()
    dataset.drop(columns=['Asset Class'], inplace=True)
    # Everything is in USD, so drop that feature
    dataset.drop(columns=['Currency'], inplace=True)
    # Keep only companies in NASDAQ and NYSE
    exchanges_to_keep = ['NASDAQ', 'New York Stock Exchange Inc.']
    dataset = dataset[dataset['Exchange'].isin(exchanges_to_keep)].copy()
    # Drop 'ShortTermDebtOrCurrentLiab': 40% missing values
    quarters = ['_2024Q2', '_2024Q3', '_2024Q4', '_2025Q1', '_2025Q2']
    columns_to_drop = ['ShortTermDebtOrCurrentLiab' + quarter for quarter in quarters]
    dataset.drop(columns=columns_to_drop, inplace=True)
    # Drop companies where key variables are zero (90 total)
    non_zero_cols = ['Revenue', 'TotalAssets', 'TotalEquity', 'CurrentLiabilities']
    indexes_to_drop = set()
    for column in non_zero_cols:
        for quarter in quarters:
            index_where_zero = dataset[dataset[column + quarter] == 0].index
        for index in index_where_zero:
            indexes_to_drop.add(index)
    dataset.drop(index=indexes_to_drop, inplace=True)
    return dataset

def market_cap_categories(dataset: pd.DataFrame) -> pd.DataFrame:
    """Adds market cap categories to the dataframe."""
    caps = (dataset['Market Value']
        .astype(str)
        .str.replace(r'[^0-9.\-eE]', '', regex=True))
    caps = pd.to_numeric(caps, errors='coerce')
    
    # Create the market cap bins. Looks like the market value is in thousands of dollars so we need to actually adjust our bins down by 1000
    bins = np.array([0, 50e6, 250e6, 2e9, 10e9, 200e9, np.inf]) / 1e3
    # Create the labels for the market caps
    labels = ['Nano-Cap','Micro-Cap','Small-Cap','Mid-Cap','Large-Cap','Mega-Cap']
    
    # Apply to the dataset
    dataset['Market Cap'] = pd.cut(caps, bins=bins, labels=labels, right=False, include_lowest=True)
    return dataset
    
if __name__ == '__main__':
    # Get command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input_file', help='name of input file: Russell_3000_With_Macro.csv'
    )
    parser.add_argument(
        'output_file', help='Title of output file: Russell_3000_Cleaned.csv'
    )
    args = parser.parse_args()
    # Load input file, clean dataframe, and write output file
    df = pd.read_csv(args.input_file)
    cleaned_df = clean(df)
    cleaned_df = market_cap_categories(cleaned_df)
    print("Added Market Cap Categories to DataFrame")
    cleaned_df.to_csv(args.output_file, index=False)
    print(f"Cleaned file saved to {args.output_file}")

