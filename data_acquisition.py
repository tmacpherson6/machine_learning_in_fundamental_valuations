'''
This is going to be the first file in the pipeline for our dataset creation and preparation for the machine learning model.

It will load the Russell 3000 data and update with additional financial data.

The output will be a csv file that will be used in the next step of the pipeline.
'''

import argparse
import numpy as np
import pandas as pd
import yfinance as yf



def download_stock_data(input_file: str, output_file: str) -> None:
    """
    Downloads the Base Stock CSV data from the Repoository. In this project
    we use the Russell 3000 ETF as our base stock data. The data 
    is downloaded from:
    https://www.ishares.com/us/products/239714/ishares-russell-3000-etf

    The base data should contain:  
    - Ticker  
    - Company Name  
    - Sector  
    - Asset Class  
    - Market Value (Market Cap, quantitative)  
    - Weight (%) in the ETF  
    - Notional Value (Equal to Market Value)  
    - Quantity (Number of Outstanding Shares)
    - Price (Current Price per Share at time of download)
    - Location (Headquarters)
    - Exchange (Primary Exchange)
    - Currency (Trading Currency)

    Parameters:
    input_file (str): The original Stock CSV file path.
    """
    # Load the Russell 3000 data from the provided CSV file
    df = pd.read_csv(input_file)

    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help = 'Title of input file: Russell_3000.csv')
    parser.add_argument('output_file', help = 'Title of output file. ')
    args = parser.parse_args()

    # Set the output file name and export the data
    input_file = args.input_file
    df = download_stock_data(args.input_file, args.output_file)
    print(df.shape)


    # Screen logging on the completion of the download
    #print(f"Data downloaded and saved to {args.output_file}")
    