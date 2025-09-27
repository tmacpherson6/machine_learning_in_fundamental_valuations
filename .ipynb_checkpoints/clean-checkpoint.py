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

from helpers import get_quarters, string_to_float


def clean(input_df: pd.DataFrame) -> pd.DataFrame:
    """Cleans the dataframe.
    
    This function is not very modular.  It uses column names that are
    specific to the Russell_3000 data. 
    """
    dataset = input_df.copy()
    quarters = get_quarters(dataset)
    # Drop duplicates
    dataset.drop_duplicates(inplace=True)
    duplicated_rows = dataset[dataset.duplicated()]
    print(f'Duplicated rows remaining: {duplicated_rows.shape[0]}')
          
    # Drop where ticker is duplicated
    duplicates = dataset.loc[(
        dataset.duplicated('Ticker', keep=False)
    )].sort_values('Ticker')
    dataset.drop(index=list(duplicates.index), inplace=True)
    duplicated_Tickers = dataset[dataset.duplicated('Ticker')]
    print(f'Duplicated Tickers remaining: {duplicated_Tickers.shape[0]}')
    
    # Keep only entries that are classified as Equity
    dataset = dataset[dataset['Asset Class'] == 'Equity'].copy()
    print(f'Asset Classes remaining: {dataset['Asset Class'].unique()}')
    
    # Keep only companies in NASDAQ and NYSE
    exchanges_to_keep = ['NASDAQ', 'New York Stock Exchange Inc.']
    dataset = dataset[dataset['Exchange'].isin(exchanges_to_keep)].copy()
    print(f'Exchanges remaining: {dataset.Exchange.unique()}')
    
   # Drop companies where key variables are zero (90 total in Russell_3000)
    non_zero_cols = ['Revenue',
                     'NetIncome',
                     'CurrentAssets',
                     'CurrentLiabilities',
                     'TotalAssets',
                     'TotalLiabilities',
                     'TotalEquity',
                     'TotalDebt',
                     'CashFromOps'
                    ]
    indexes_to_drop = set()
    for column in non_zero_cols:
        for quarter in quarters:
            index_where_zero = dataset[dataset[column + quarter] == 0].index
            for index in index_where_zero:
                indexes_to_drop.add(index)
    dataset.drop(index=indexes_to_drop, inplace=True)
    print(f'Dropped {len(indexes_to_drop)} rows with value zero (0) in: {non_zero_cols}.')
    zeros_remaining = 0
    for column in non_zero_cols:
        for quarter in quarters:
            zeros_remaining += dataset[column + quarter][dataset[column + quarter] == 0].shape[0]
    print(f'Number of zero values remaining in key columns: {zeros_remaining}')
    
    # Modify Location using One-Hot-Encoding
    # 1 = company in U.S., 0 = company outside U.S.
    locations = [location for location in dataset['Location'].unique()]
    replace_dict = {}
    for location in locations:
        if location == 'United States':
            replace_dict[location] = 1
        else:
            replace_dict[location] = 0
    dataset['Location'] = dataset['Location'].replace(replace_dict)
    new_locations = dataset.Location.unique()
    print(f'Unique values for Location (1=U.S., 0=outside U.S.): {new_locations}')
        
    # Convert columns with string values to floating point
    for column in ['Market Value']:
        dataset[column] = string_to_float(dataset[column])
    print(f'Market Value is now of type {dataset['Market Value'].dtype}')
    
    # Drop unnecessary or problematic columns
    columns_to_drop = ['ShortTermDebtOrCurrentLiab' + quarter for quarter in quarters]
    columns_to_drop = ['OriginalTicker',
                       'YahooSymbol',
                       'Asset Class',
                       'Currency',
                       'Weight (%)',
                       'Price',
                       'Quantity',
                       'Notional Value'
                      ] + columns_to_drop
    dataset.drop(columns=columns_to_drop, inplace=True)
    print('\nDropped the following columns:')
    for column in columns_to_drop:
        print(column)

    # Report final status
    print('\nColumns remaining:')
    for column in dataset.columns:
        print(column)
    print(f'{dataset.shape[1]} columns (features) remaining.')
    print(f'{dataset.shape[0]} rows (companies) remaining.')
    return dataset


def market_cap_categories(dataset: pd.DataFrame) -> pd.DataFrame:
    """Adds market cap categories to the dataframe."""
    caps = (dataset['Market Value']
        .astype(str)
        .str.replace(r'[^0-9.\-eE]', '', regex=True))
    caps = pd.to_numeric(caps, errors='coerce')
    
    # Create the market cap bins. Looks like the market value is in thousands of dollars
    # so we need to actually adjust our bins down by 1000
    bins = np.array([0, 50e6, 250e6, 2e9, 10e9, 200e9, np.inf]) / 1e3
    # Create the labels for the market caps
    labels = ['Nano-Cap','Micro-Cap','Small-Cap','Mid-Cap','Large-Cap','Mega-Cap']
    
    # Apply to the dataset
    dataset['Market Cap'] = pd.cut(caps, bins=bins, labels=labels, right=False, include_lowest=True)
    return dataset


pd.set_option("future.no_silent_downcasting", True)

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
    print(f'\nCleaning ' + args.input_file + '...')
    cleaned_df = clean(df)
    cleaned_df = market_cap_categories(cleaned_df)
    print('Added Market Cap Categories to DataFrame')
    cleaned_df.to_csv(args.output_file, index=False)
    print(f'\nCleaned file saved to {args.output_file}')
