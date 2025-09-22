"""Clean company financial and macro data.

Command Line usage (example for Linux):
 python clean.py <in_file.csv> <out_file.csv>
Notes:
 <in_file.csv> -- the CSV file to be cleaned by this module
 <out_file.csv. -- the cleaned CSV file to write to disk
"""
import argparse

import pandas as pd


def clean(input_df: pd.DataFrame) -> pd.DataFrame:
    """Cleans the dataframe.
    
    This function is not very modular.  It uses column names that are
    specific to the Russell_3000.csv data file. 
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
    cleaned_df.to_csv(args.output_file, index=False)
    print(f"Cleaned file saved to {args.output_file}")

