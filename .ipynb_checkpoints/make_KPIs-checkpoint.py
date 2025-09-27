"""Create Key Performance Indicators (KPI) from company financial data.

Command Line usage (example for Linux):
 python make_KPIs.py <in_file.csv> <out_file.csv>
Notes:
 <in_file.csv> -- CSV file with company fundamentals data
 <out_file.csv. -- CSV file augmented with KPIs
"""
import argparse

import pandas as pd

from helpers import get_quarters
    

def make_KPIs(input_df: pd.DataFrame) -> pd.DataFrame:
    """Adds key performance indicators (KPI) to the dataset.

    Based on recommendations from Harvard Business School (HBS),
    https://online.hbs.edu/blog/post/financial-performance-measures
    
    Note: this function is not very modular; it uses column names that are
    specific to the Russell_3000 data.
    """
    dataset = input_df.copy()
    quarters = get_quarters(dataset)
    # Gross Profit Margin = (Revenue - Cost of Revenue) / Revenue
    KPI = 'KPI_GrossProfitMargin'
    for quarter in quarters:
        dataset[KPI + quarter] = (
            dataset['Revenue' + quarter] - dataset['CostOfRevenue' + quarter]
        ) / dataset['Revenue' + quarter]
    # Net Profit Margin = Net Profit / Revenue
    KPI = 'KPI_NetProfitMargin'
    for quarter in quarters:
        dataset[KPI + quarter] = (
            dataset['NetIncome' + quarter] / dataset['Revenue' + quarter]
        )
    # Working Capital = Current Assets - Current Liabilities
    KPI = 'KPI_WorkingCapital'
    for quarter in quarters:
        dataset[KPI + quarter] = (
            dataset['CurrentAssets' + quarter]
            - dataset['CurrentLiabilities' + quarter]
        )
    # Current Ratio = Current Assets / Current Liabilities
    KPI = 'KPI_CurrentRatio'
    for quarter in quarters:
        dataset[KPI + quarter] = (
            dataset['CurrentAssets' + quarter]
            / dataset['CurrentLiabilities' + quarter]
        )
    # Leverage = Total Assets / Total Equity
    KPI = 'KPI_Leverage'
    for quarter in quarters:
        dataset[KPI + quarter] = (
            dataset['TotalAssets' + quarter]
            / dataset['TotalEquity' + quarter]
        )
    # Debt-to-Equity Ratio = Total Debt / Total Equity
    KPI = 'KPI_DebtToEquityRatio'
    for quarter in quarters:
        dataset[KPI + quarter] = (
            dataset['TotalDebt' + quarter] / dataset['TotalEquity' + quarter]
        )
    # Total Asset Turnover = Revenue / ((Beg Total Assets + End Total Assets) / 2)
    KPI = 'KPI_TotalAssetTurnover'
    for i in range(len(quarters) - 1):
        beg, end = i, i + 1
        dataset[KPI + quarters[end]] = (
            dataset['Revenue' + quarters[end]] / ((
                dataset['TotalAssets' + quarters[beg]]
                + dataset['TotalAssets' + quarters[end]]
            ) / 2)
        )
    # Return on Equity (ROE) = Net Profit / ((Beg Equity + End Equity) / 2)
    KPI = 'KPI_ReturnOnEquity'
    for i in range(len(quarters) - 1):
        beg, end = i, i + 1
        dataset[KPI + quarters[end]] = (
            dataset['NetIncome' + quarters[end]] / ((
                dataset['TotalEquity' + quarters[beg]]
                + dataset['TotalEquity' + quarters[end]]
            ) / 2)
        )
    # Return on Assets (ROA) = Net Profit / ((Beg Total Assets + End Total Assets) / 2)
    KPI = 'KPI_ReturnOnAssets'
    for i in range(len(quarters) - 1):
        beg, end = i, i + 1
        dataset[KPI + quarters[end]] = (
            dataset['NetIncome' + quarters[end]] / ((
                dataset['TotalAssets' + quarters[beg]]
                + dataset['TotalAssets' + quarters[end]]
            ) / 2)
        )
    # Cash Flow = Cash From Operations
    KPI = 'KPI_CashFlow'
    for quarter in quarters:
        dataset[KPI + quarter] = dataset['CashFromOps' + quarter]
    # Return final dataframe
    return dataset


if __name__ == '__main__':
    # Get command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input_file', help='name of input file: X_train_filled.csv, or X_test_filled.csv'
    )
    parser.add_argument(
        'output_file', help='name of output file: X_train_filled_KPIs.csv, or X_test_filled_KPIs.csv'
    )
    args = parser.parse_args()
    # Load input file, clean dataframe, and write output file
    df = pd.read_csv(args.input_file)
    KPI_df = make_KPIs(df)
    KPI_df.to_csv(args.output_file, index=False)
    print(f"KPI file saved to {args.output_file}")
