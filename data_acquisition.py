'''
This is going to be the first file in the pipeline for our dataset creation and preparation for the machine learning model.

It will load the Russell 3000 data and update with additional financial data.

The output will be a csv file that will be used in the next step of the pipeline.
'''

import argparse
import numpy as np
import pandas as pd
import yfinance as yf
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed



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
    # Load the Base Stock data from the provided CSV file
    df = pd.read_csv(input_file)

    return df

def build_ticker_mapping(df):
    """
    Build a mapping from OriginalTicker list from our original CSV to YahooSymbol
    """
    if "Ticker" not in df.columns:
        raise KeyError("Your DataFrame must have a 'Ticker' column.")
    orig_tickers = (
        df["Ticker"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

    return orig_tickers

def fetch_metrcis(orig_tickers, max_workers=8):
    """
    Fetch financial metrics for a list of original tickers using multithreading.
    """
    rows = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(fetch_last_completed_quarters, tk): tk for tk in orig_tickers}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="Fetching last 5 completed-quarter metrics"):
            rows.append(fut.result())
    
    metrics = pd.DataFrame(rows)
    return metrics

def _label_quarter(ts):
    """
    Convert a timestamp to a 'YYYYQ#' quarter label.
    """
    ts = pd.Timestamp(ts)
    q = (ts.month - 1)//3 + 1
    return f"{ts.year}Q{q}"

def _last_completed_quarter(as_of=None):
    """
    Return (year, quarter) for the most recently COMPLETED quarter relative to as_of.
    """
    if as_of is None:
        as_of = pd.Timestamp.today()
    y = as_of.year
    q = (as_of.month - 1)//3 + 1
    # current quarter is in-progress -> use previous quarter
    if q > 1:
        return y, q - 1
    else:
        return y - 1, 4

def _last_n_completed_quarters(n=5, as_of=None):
    """
    Return list of 'YYYYQ#' labels for the last n COMPLETED quarters (most recent first).
    most recent -> oldedr
    """
    y, q = _last_completed_quarter(as_of)
    labels = []
    for _ in range(n):
        labels.append(f"{y}Q{q}")
        if q > 1:
            q -= 1
        else:
            q = 4
            y -= 1
    return labels

def _get_series(df, candidates, max_quarters=8):
    """
    Return a Series for the first matching row in `candidates`, indexed by period end,
    sorted ascending by date (we'll filter by ALLOWED_QUARTERS later).
    Works for income_stmt, cashflow, and balance_sheet frames.
    """
    if df is None or not hasattr(df, "index") or df.empty:
        return pd.Series(dtype=float)
    row = next((r for r in candidates if r in df.index), None)
    if row is None:
        return pd.Series(dtype=float)
    s = df.loc[row].dropna()
    try:
        s.index = pd.to_datetime(s.index)
    except Exception:
        pass
    return s.sort_index().tail(max_quarters)

def fetch_last_completed_quarters(orig_ticker, retries=2, pause=0.3):
    """
    Pull metrics only for the last 5 COMPLETED quarters (exclude the current quarter).
    Includes Income/CF metrics and Balance Sheet metrics.
    """
    ytk = yahoo_map.get(orig_ticker, orig_ticker)
    for _ in range(retries + 1):
        try:
            t = yf.Ticker(ytk)
            inc = getattr(t, "quarterly_income_stmt", None)
            cf  = getattr(t, "quarterly_cashflow", None)
            bal = getattr(t, "quarterly_balance_sheet", None)

            # Income & CF series
            rev = _get_series(inc, REV)
            opi = _get_series(inc, OPI)
            net = _get_series(inc, NET)
            eps = _get_series(inc, EPS)  # may be empty; OK
            cfo = _get_series(cf,  CFO)

            # Balance sheet series (NEW)
            cash   = _get_series(bal, CASH)
            assets = _get_series(bal, ASSETS)
            liab   = _get_series(bal, LIAB)
            stdebt = _get_series(bal, ST_DEBT)
            ltdebt = _get_series(bal, LT_DEBT)
            equity = _get_series(bal, EQUITY)

            row = {"OriginalTicker": orig_ticker, "YahooSymbol": ytk}

            for series, metric in [
                (rev,   "Revenue"),
                (opi,   "OperatingIncome"),
                (net,   "NetIncome"),
                (cfo,   "CashFromOps"),
                (eps,   "EPS"),
                (cash,  "CashAndSTInvestments"),
                (assets,"TotalAssets"),
                (liab,  "TotalLiabilities"),
                (stdebt,"ShortTermDebtOrCurrentLiab"),
                (ltdebt,"LongTermDebt"),
                (equity,"TotalEquity"),
            ]:
                if series is None or series.empty:
                    continue
                for dt, val in series.items():
                    q = _label_quarter(dt)
                    if q in ALLOWED_QUARTERS:
                        # EPS might already be float; others may be numpy types
                        try:
                            row[f"{metric}_{q}"] = float(val)
                        except Exception:
                            # if conversion fails, skip this value gracefully
                            continue
            return row
        except Exception:
            time.sleep(pause)

    return {"OriginalTicker": orig_ticker, "YahooSymbol": ytk}




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help = 'Title of input file: Russell_3000.csv')
    parser.add_argument('output_file', help = 'Title of output file. ')
    args = parser.parse_args()

    # Set the output file name and export the data
    input_file = args.input_file
    df = download_stock_data(args.input_file, args.output_file)

    # Optional: symbol mapping if your tickers differ from Yahoo (leave empty if not needed)
    yahoo_map = {}  # e.g., {'BRK.B': 'BRK-B'}
    
    # Candidate labels (Yahoo varies naming sometimes)
    # Income / CF (existing)
    REV = ["Total Revenue","TotalRevenue","Revenue","Operating Revenue","OperatingRevenue"]
    OPI = ["Operating Income","OperatingIncome","Operating Income (Loss)","OperatingIncomeLoss"]
    NET = ["Net Income","NetIncome","Net Income Common Stockholders","NetIncomeCommonStockholders",
        "Net Income Applicable To Common Shares","NetIncomeApplicableToCommonShares"]
    CFO = ["Operating Cash Flow","OperatingCashFlow","Total Cash From Operating Activities",
        "Net Cash Provided by Operating Activities","NetCashProvidedByUsedInOperatingActivities"]
    EPS = ["Diluted EPS","DilutedEPS","Basic EPS","BasicEPS","EPS (Diluted)","EarningsPerShare"]
    
    # Balance Sheet (NEW)
    CASH   = ["Cash And Cash Equivalents", "CashCashEquivalentsAndShortTermInvestments", "Cash And Short Term Investments"]
    ASSETS = ["Total Assets","TotalAssets"]
    LIAB   = ["Total Liabilities Net Minority Interest","TotalLiabilitiesNetMinorityInterest","Total Liabilities"]
    ST_DEBT = ["Current Debt","CurrentDebt","Short Term Debt","ShortTermDebt",
            "Total Current Liabilities","Current Portion Of Long Term Debt"]
    LT_DEBT = ["Long Term Debt","LongTermDebt","Non Current Debt","NonCurrentDebt",
            "Long Term Debt And Capital Lease Obligation"]
    EQUITY = ["Total Stockholder Equity","TotalStockholderEquity","StockholdersEquity",
            "Total Equity Gross Minority Interest","TotalEquityGrossMinorityInterest"]
    
    # Build allowed quarter labels (exclude current quarter)
    ORDERED_QUARTERS = _last_n_completed_quarters(n=5)  # e.g., ['2025Q2','2025Q1','2024Q4','2024Q3','2024Q2']
    ALLOWED_QUARTERS = set(ORDERED_QUARTERS)

    orig_tickers = build_ticker_mapping(df)
    print(f"Found {len(orig_tickers)} unique tickers to process from your original CSV file.")
    
    metrics = fetch_metrcis(orig_tickers, max_workers=8)
    print(f"Fetched financial metrics for {len(metrics)} tickers.")

    
    # Screen logging on the completion of the download
    #print(f"Data downloaded and saved to {args.output_file}")
    