import pandas as pd
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('train_input', help='Path to old CSV file with reference values')
    parser.add_argument('test_input', help='Path to new CSV file to process')
    parser.add_argument('train_output', help='Output file for the original method (self-fill)')
    parser.add_argument('test_output', help='Output file for the new method (use old file medians)')
    args = parser.parse_args()

    # Load datasets
    df_train = pd.read_csv(args.train_input)
    df_test = pd.read_csv(args.test_input)

    # Fundamental prefixes
    fundamental_prefixes = [
        "CapitalExpenditure", "CashAndSTInvestments", "CashFromOps", "CostOfRevenue",
        "CurrentAssets", "CurrentLiabilities", "EPS", "IncomeTaxExpense", "InterestExpense",
        "LongTermDebt", "NetIncome", "OperatingIncome", "OtherOperatingExpense",
        "Revenue", "TotalAssets", "TotalDebt", "TotalEquity", "TotalLiabilities"
    ]

    # Pick relevant columns
    target_cols_old = [c for c in df_train.columns if any(c.startswith(p + "_") for p in fundamental_prefixes)]
    target_cols_new = [c for c in df_test.columns if any(c.startswith(p + "_") for p in fundamental_prefixes)]

    # --- 1. Original method (self-fill within test_input itself) ---
    df_original_train = df_train.copy()
    for col in target_cols_new:
        df_original_train[col] = df_original_train.groupby(['Sector','Market Cap'])[col].transform(lambda s: s.fillna(s.median()))
    df_original_train = df_original_train.dropna()
    df_original_train.to_csv(args.train_output, index=False)

    # --- 2. New method (fill using medians from train_input) ---
    df_new_test = df_test.copy()
    for col in target_cols_new:
        medians = df_train.groupby(['Sector','Market Cap'])[col].median()
        df_new_test[col] = df_new_test.apply(
            lambda row: medians.get((row['Sector'], row['Market Cap']), pd.NA) if pd.isna(row[col]) else row[col],
            axis=1
        )
    df_new_test = df_new_test.dropna()
    df_new_test.to_csv(args.test_output, index=False)

    print("✅ Processing complete!")
    print(f"Original-style output saved to {args.train_output}")
    print(f"New-style output saved to {args.test_output}")
