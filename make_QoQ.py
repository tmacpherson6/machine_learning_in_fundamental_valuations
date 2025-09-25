'''
This python script is used to perform feature engineering on a dataset containing financial and macroeconomic data. The script reads in training and testing datasets, processes the data to create new features based on quarter-over-quarter (QoQ) changes and raw values, and handles missing data. Finally, it saves the processed datasets to CSV files for further analysis or modeling.
'''

import argparse
import numpy as np
import pandas as pd
from data_acquisition import upload_file, save_to_csv



def get_unique_columns(columns):
    unique_columns = set()
    for column in columns:
        column = column.replace(' ','_')
        words = column.split('_')
        if words[0] != 'KPI':
            unique_columns.add(words[0])
        else:
            unique_columns.add(str(words[0]) + '_' + str(words[1]))
    unique_columns = list(unique_columns)
    
    # Remove non-repetitive columns
    drop = {'Name','Ticker','Exchange','Sector','Market','Location','Inflation','Unemployment','IndustrialProd','GDP','GDPReal','InterestRate'}
    
    unique_columns = [c for c in unique_columns if c not in drop]

    return unique_columns


def quarterly_changes(dataset, unique_columns, quarters):
    for column in unique_columns:
        try:
            for val in range(1,len(quarters)):
                series_1 = dataset[str(column) + str(quarters[val-1])]
                series_2 = dataset[str(column) + str(quarters[val])]
                dataset[f'{column}_QoQ_{quarters[val-1][-4:]}_{quarters[val][-4:]}'] = (series_2 - series_1)/series_1
        except:
            for val in range(2,len(quarters)):
                series_1 = dataset[str(column) + str(quarters[val-1])]
                series_2 = dataset[str(column) + str(quarters[val])]
                dataset[f'{column}_QoQ_{quarters[val-1][-4:]}_{quarters[val][-4:]}'] = (series_2 - series_1)/series_1

    print(f"Completed Quarterly Change Calculations")
    return dataset



def get_rate_columns(train_dataset: pd.DataFrame):
    columns = train_dataset.columns
    # Use sets to avoid duplicates
    QoQ_columns = set()
    QoQ_quarters = set()
    for column in columns:
        if 'QoQ' in column:
            # Pull out the common Column Name
            QoQ_columns.add(column[:-10])
            # Let's also pull out the QoQ
            QoQ_quarters.add(column[-10:])
    QoQ_columns = list(QoQ_columns)
    QoQ_quarters = list(QoQ_quarters)
    # Order will be important so let's sort them
    QoQ_quarters.sort()
    return QoQ_columns, QoQ_quarters


def safe_slope(vals: list[float]) -> float:
    a = np.asarray(vals, float)
    a = a[np.isfinite(a)]
    n = a.size
    if n < 2:
        return np.nan
    t = np.arange(n, dtype=float)
    
    # OLS slope without lstsq
    St, Sy = t.sum(), a.sum()
    Stt, Sty = (t*t).sum(), (t*a).sum()
    denom = n*Stt - St*St
    if np.isclose(denom, 0.0):
        return 0.0
    
    return (n*Sty - St*Sy) / denom

def get_rate_data(row, cols, quarters):
    for col in cols:
        vals = [row.get(f"{col}{q}", np.nan) for q in quarters]
        row[f"{col}_Rate"] = safe_slope(vals)
    return row







if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_train_file', help = 'Title of input training file: X_train_filled_KPIs.csv')
    parser.add_argument('input_test_file', help = 'Title of input training file: X_test_filled_KPIs.csv')
    parser.add_argument('output_train_file', help = 'Title of input training file: X_train_filled_KPIs_QoQ.csv')
    parser.add_argument('output_test_file', help = 'Title of input training file: X_test_filled_KPIs_QoQ.csv')
    args = parser.parse_args()

    # Set the output file name and export the data
    train_dataset = upload_file(args.input_train_file)
    test_dataset = upload_file(args.input_test_file)
    
    # Get rid of the index column
    train_dataset.drop(columns=['Unnamed: 0'], inplace=True)
    test_dataset.drop(columns=['Unnamed: 0'], inplace=True)

    columns = train_dataset.columns.tolist()
    quarters = ['_2024Q2','_2024Q3','_2024Q4','_2025Q1']
    unique_columns = get_unique_columns(columns)
    #print(unique_columns)

    train_dataset = quarterly_changes(train_dataset, unique_columns, quarters)
    test_dataset = quarterly_changes(test_dataset, unique_columns, quarters)
    #print(train_dataset.shape)

    # Now let's get the QoQ columns
    QoQ_columns, QoQ_quarters = get_rate_columns(train_dataset)
    
    # Now let's get the rate data
    train_dataset = train_dataset.apply(lambda r: get_rate_data(r, QoQ_columns, QoQ_quarters), axis=1)
    train_dataset = train_dataset.apply(lambda r: get_rate_data(r, unique_columns, quarters), axis=1)
    test_dataset = test_dataset.apply(lambda r: get_rate_data(r, QoQ_columns, QoQ_quarters), axis=1)
    test_dataset = test_dataset.apply(lambda r: get_rate_data(r, unique_columns, quarters), axis=1)
    print(train_dataset.shape)

    # Save the data to a CSV file
    save_to_csv(train_dataset, args.output_train_file)
    save_to_csv(test_dataset, args.output_test_file)