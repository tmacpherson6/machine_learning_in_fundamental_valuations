'''
Get Macroeconomic data from the St. Louis Fed (FRED API). Then merge macroeconomic data to the dataset.
'''

import argparse

import pandas as pd

from fredapi import Fred
from data_acquisition import upload_file
from data_acquisition import save_to_csv

fred_api_key = "0fd09a8eca4539118cb3699daec8667a"

def get_macro_data(api_key: str) -> pd.DataFrame:
    # Get all of the macroeconomic data from FRED  
    fred = Fred(api_key = fred_api_key)
    GDP = fred.get_series("GDP")[-6:]
    GDPReal = fred.get_series("GDPC1")[-6:]
    Unemployment = fred.get_series("UNRATE").resample("QS").mean()[-7:-1]
    InterestRate = fred.get_series("FEDFUNDS").resample("QS").mean()[-7:-1]
    IndustrialProd = fred.get_series("INDPRO").resample("QS").mean()[-7:-1]
    Inflation = fred.get_series("CPIAUCSL").resample('QS').mean()[-7:-1]
    
    # Create a DataFrame with the macroeconomic data
    row_data = {
        "GDP": GDP,
        "GDPReal": GDPReal,
        "Unemployment": Unemployment,
        "InterestRate": InterestRate,
        "IndustrialProd": IndustrialProd,
        "Inflation": Inflation,
    }
    quarters = ['_2024Q1','_2024Q2','_2024Q3','_2024Q4','_2025Q1']
    
    macro = {f"{name}{q}": float(v)
            for name, s in row_data.items()
            for q, v in zip(quarters, s)}
    
    macro_data = pd.DataFrame([macro])
    return macro_data

def merge_macro_data(df: pd.DataFrame, macro_data: pd.DataFrame) -> pd.DataFrame:
    # Merge the macroeconomic data with the existing DataFrame
    for col in macro_data.columns:
        df[col] = macro_data.iloc[0][col]
    return df



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help = 'Title of input file: Russell_3000.csv')
    parser.add_argument('output_file', help = 'Title of output file. ')
    args = parser.parse_args()

    # Set the output file name and export the data
    input_file = args.input_file
    df = upload_file(args.input_file)
    
    # Get the macroeconmic data
    macro_data = get_macro_data(fred_api_key)
    print(f"Macroeconomic Data Obtained:\n{macro_data}\n")

    # Merge the macroeconomic data with the existing DataFrame
    df = merge_macro_data(df, macro_data)
    print('Merged DataFrame with Macroeconomic Data')

    # Save the updated DataFrame to a new CSV file
    save_to_csv(df, args.output_file)
    print(f"Data with Macroeconomic Data saved to {args.output_file}")

