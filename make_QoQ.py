'''
This python script is used to perform feature engineering on a dataset containing financial and macroeconomic data. The script reads in training and testing datasets, processes the data to create new features based on quarter-over-quarter (QoQ) changes and raw values, and handles missing data. Finally, it saves the processed datasets to CSV files for further analysis or modeling.
'''

import argparse
import numpy as np
import pandas as pd
from typing import Iterable, List, Sequence, Tuple
from data_acquisition import upload_file, save_to_csv



def get_unique_columns(columns: Iterable[str]) -> List[str]:
    """
    Derive base feature names from a list of column labels.

    Logic:
      - Replace spaces with underscores.
      - If the column starts with 'KPI_', keep the first two tokens ('KPI_<name>').
      - Otherwise keep only the first token before the first underscore.
      - Drop non-repetitive identifiers (e.g., Name, Ticker, macro singletons).

    Parameters
    ----------
    columns : Iterable[str]
        Original column names (e.g., 'Revenue_2025Q2', 'KPI_Margin_2025Q2').

    Returns
    -------
    List[str]
        Unique base column names to iterate over (e.g., ['Revenue', 'KPI_Margin', ...]).
    """
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


def quarterly_changes(
    dataset: pd.DataFrame,
    unique_columns: Sequence[str],
    quarters: Sequence[str],
) -> pd.DataFrame:
    """
    Create QoQ change features for each base column across consecutive quarters.

    For each base `column`, computes:
        {column}_QoQ_{q_{t-1}[-4:]}_{q_t[-4:]} = (value_t - value_{t-1}) / value_{t-1}

    Notes
    -----
    - Mutates `dataset` in place by adding new QoQ columns and also returns it.
    - Broad try/except is used to handle series that start later (no first quarter).

    Parameters
    ----------
    dataset : pd.DataFrame
        Wide table with per-quarter columns like '<column><quarter>'.
    unique_columns : Sequence[str]
        Base names to compute QoQ for (e.g., ['Revenue', 'KPI_Margin']).
    quarters : Sequence[str]
        Ordered quarter suffixes (e.g., ['_2024Q2','_2024Q3','_2024Q4','_2025Q1']).

    Returns
    -------
    pd.DataFrame
        The same DataFrame with additional QoQ feature columns.
    """
    for column in unique_columns:
        try:
            for val in range(1,len(quarters)):
                series_1 = dataset[str(column) + str(quarters[val-1])]
                series_2 = dataset[str(column) + str(quarters[val])]
                denom = series_1.replace(0.0, 0.00000001)
                qoq = (series_2 - series_1)/denom
                #What if both were zero?
                both_zero = (series_1 == 0.0) & (series_2 == 0.0)
                qoq = qoq.mask(both_zero, 0.0)
                # If numbers blow up incredibly large lets clip them to 100,000%
                qoq = qoq.clip(-1000.0, 1000.0)

                dataset[f'{column}_QoQ_{quarters[val-1][-4:]}_{quarters[val][-4:]}'] = qoq
        except:
            for val in range(2,len(quarters)):
                series_1 = dataset[str(column) + str(quarters[val-1])]
                series_2 = dataset[str(column) + str(quarters[val])]
                
                denom = series_1.replace(0.0, 0.00000001)
                qoq = (series_2 - series_1)/denom
                #What if both were zero?
                both_zero = (series_1 == 0.0) & (series_2 == 0.0)
                qoq = qoq.mask(both_zero, 0.0)
                # If numbers blow up incredibly large lets clip them to 100,000%
                qoq = qoq.clip(-1000.0, 1000.0)

                dataset[f'{column}_QoQ_{quarters[val-1][-4:]}_{quarters[val][-4:]}'] = qoq

    print(f"Completed Quarterly Change Calculations")
    return dataset



def get_rate_columns(train_dataset: pd.DataFrame) -> Tuple[List[str], List[str]]:
    """
    Infer QoQ source columns and their quarter suffixes from existing QoQ feature names.

    Expects QoQ feature columns named like:
        '<Base>_QoQ_<YYYYQx>_<YYYYQy>'
    Example: 'Revenue_QoQ_2024Q3_2024Q4'

    Parameters
    ----------
    train_dataset : pd.DataFrame
        DataFrame containing QoQ columns.

    Returns
    -------
    Tuple[List[str], List[str]]
        - QoQ base columns (e.g., ['Revenue', 'KPI_Margin', ...])
        - Sorted list of quarter window suffixes (the trailing 10 chars), e.g.,
          ['_2024Q1_2024Q2', '_2024Q2_2024Q3', ...]
    """
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


def safe_slope(vals: Sequence[float]) -> float:
    """
    Compute the OLS slope of a sequence against t = 0..n-1, robust to NaN/Inf.

    Parameters
    ----------
    vals : Sequence[float]
        Numeric series values ordered in time.

    Returns
    -------
    float
        Slope of y ~ a + b * t. Returns NaN if <2 finite points.
        Returns 0.0 if the design becomes singular.
    """
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

def get_rate_data(
    row: pd.Series,
    cols: Sequence[str],
    quarters: Sequence[str],
) -> pd.Series:
    """
    Row-wise helper to compute per-column growth 'Rate' using `safe_slope`.

    For each base name `col`, collects values from the concatenated quarter
    columns `f"{col}{q}"` for q in `quarters`, filters to finite values,
    and writes `f"{col}_Rate"` back into the row.

    Parameters
    ----------
    row : pd.Series
        A single DataFrame row (use with `df.apply(..., axis=1)`).
    cols : Sequence[str]
        Base column names to process.
    quarters : Sequence[str]
        Ordered quarter suffixes to fetch for each base column.

    Returns
    -------
    pd.Series
        The same row with additional '<col>_Rate' fields.
    """
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
    
    train_dataset.set_index('Ticker',inplace=True)
    test_dataset.set_index('Ticker',inplace=True)
    
    # Save the data to a CSV file
    save_to_csv(train_dataset, args.output_train_file, index=True)
    save_to_csv(test_dataset, args.output_test_file, index=True)
    print("Calculated QoQ ratios and exported CSV files")