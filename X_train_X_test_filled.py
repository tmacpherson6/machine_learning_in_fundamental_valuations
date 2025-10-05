import pandas as pd
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('train_input', help='Path to train_input CSV file with reference values')
    parser.add_argument('test_input', help='Path to test_input CSV file to process')
    parser.add_argument('train_output', help='Output file for the train_output')
    parser.add_argument('test_output', help='Output file for test_output (use train set medians)')
    args = parser.parse_args()

    # Load datasets
    df_train = pd.read_csv(args.train_input)
    df_test = pd.read_csv(args.test_input)
    print(df_train.head())

    ## Fundamental prefixes
    #fundamental_prefixes = [
    #    "CapitalExpenditure", "CashAndSTInvestments", "CashFromOps", "CostOfRevenue",
    #    "CurrentAssets", "CurrentLiabilities", "EPS", "IncomeTaxExpense", "InterestExpense",
    #    "LongTermDebt", "NetIncome", "OperatingIncome", "OtherOperatingExpense",
    #    "Revenue", "TotalAssets", "TotalDebt", "TotalEquity", "TotalLiabilities"
    #]
#
    ## Pick relevant columns
    #target_cols_old = [c for c in df_train.columns if any(c.startswith(p + "_") for p in fundamental_prefixes)]
    #target_cols_new = [c for c in df_test.columns if any(c.startswith(p + "_") for p in fundamental_prefixes)]
#
    ## Fill missing values for training set
    #df_original_train = df_train.copy()
    #for col in target_cols_new:
    #    df_original_train[col] = df_original_train.groupby(['Sector','Market Cap'])[col].transform(lambda s: s.fillna(s.median()))
    #df_original_train = df_original_train.dropna()
    #df_original_train.to_csv(args.train_output, index=False)
#
    ## Fill missing values for test set using medians from training set
    #df_new_test = df_test.copy()
    #for col in target_cols_new:
    #    medians = df_train.groupby(['Sector','Market Cap'])[col].median()
    #    df_new_test[col] = df_new_test.apply(
    #        lambda row: medians.get((row['Sector'], row['Market Cap']), pd.NA) if pd.isna(row[col]) else row[col],
    #        axis=1
    #    )
    #df_new_test = df_new_test.dropna()
    #df_new_test.to_csv(args.test_output, index=False)
#
    #print(f"Original-style output saved to {args.train_output}")
    #print(f"New-style output saved to {args.test_output}")
