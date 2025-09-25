import pandas as pd
import argparse




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help = 'Title of input file: X_train.csv')
    parser.add_argument('output_file', help = 'Title of output file. ')
    args = parser.parse_args()

    df = pd.read_csv(args.input_file)
    fundamental_prefixes = [
        "CapitalExpenditure", "CashAndSTInvestments", "CashFromOps", "CostOfRevenue",
        "CurrentAssets", "CurrentLiabilities", "EPS", "IncomeTaxExpense", "InterestExpense",
        "LongTermDebt", "NetIncome", "OperatingIncome", "OtherOperatingExpense",
        "Revenue", "TotalAssets", "TotalDebt", "TotalEquity", "TotalLiabilities"
    ]
    target_cols = [c for c in df.columns if any(c.startswith(p + "_") for p in fundamental_prefixes)]

    # Sector + Tranche
    for col in target_cols:
        df[col] = df.groupby(['Sector','Market Cap'])[col].transform(lambda s: s.fillna(s.median()))


    # Remaining NaN counts for target columns
    remaining_nans = {col: int(df[col].isna().sum()) for col in target_cols}
    df = df.dropna()
    df.to_csv(args.output_file, index=False)



