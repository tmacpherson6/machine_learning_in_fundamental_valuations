'''
This python script is used to perform feature engineering on a dataset containing financial and macroeconomic data. The script reads in training and testing datasets, processes the data to create new features based on quarter-over-quarter (QoQ) changes and raw values, and handles missing data. Finally, it saves the processed datasets to CSV files for further analysis or modeling.
'''

import argparse
import numpy as np
import pandas as pd
from data_acquisition import upload_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_train_file', help = 'Title of input training file: X_train_filled_KPIs.csv')
    parser.add_argument('input_test_file', help = 'Title of input training file: X_test_filled_KPIs.csv')
    parser.add_argument('output_train_file', help = 'Title of input training file: X_train_filled_KPIs_QoQ.csv')
    parser.add_argument('output_test_file', help = 'Title of input training file: X_test_filled_KPIs_QoQ.csv')
    args = parser.parse_args()

    # Set the output file name and export the data
    input_file = args.input_file
    df = upload_file(args.input_file)
    