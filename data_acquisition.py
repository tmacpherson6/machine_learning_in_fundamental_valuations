'''
This is going to be the first file in the pipeline for our dataset creation and preparation for the machine learning model.

It will load the Russell 3000 data and update with additional financial data.

The output will be a csv file that will be used in the next step of the pipeline.

'yfinance' has been acting up recently, in IDE's however this python script runs perfectly fine in google colab.
'''

import argparse
import time
import re

import pandas as pd
import yfinance as yf

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


def _norm(s: str) -> str:
    """Lowercase, remove non-alnum; robust to spaces/punctuation/casing."""
    _norm_re = re.compile(r"[^a-z0-9]+")
    return _norm_re.sub("", str(s).lower())

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

def _get_series_caseflex(df, candidates, keywords=None, max_quarters=8):
    """
    Robust row resolver:
      1) exact match
      2) case/space/punct-insensitive match
      3) fuzzy 'contains' search using keywords (if provided)
    Returns Series indexed by period-end (datetime), sorted asc.
    """
    if df is None or not hasattr(df, "index") or df.empty:
        return pd.Series(dtype=float)

    # 1) exact
    for r in candidates:
        if r in df.index:
            s = df.loc[r].dropna()
            try: s.index = pd.to_datetime(s.index)
            except: pass
            return s.sort_index().tail(max_quarters)

    # 2) normalized exact
    norm_to_real = { _norm(idx): idx for idx in df.index }
    for r in candidates:
        nr = _norm(r)
        if nr in norm_to_real:
            s = df.loc[norm_to_real[nr]].dropna()
            try: s.index = pd.to_datetime(s.index)
            except: pass
            return s.sort_index().tail(max_quarters)

    # 3) fuzzy contains by keywords
    if keywords:
        hits = []
        lower_idx = [(idx, idx.lower()) for idx in df.index]
        for idx, low in lower_idx:
            if any(k.lower() in low for k in keywords):
                hits.append(idx)
        if hits:
            # prefer the first stable-looking hit (shortest name as a heuristic)
            hits.sort(key=lambda x: len(x))
            s = df.loc[hits[0]].dropna()
            try: s.index = pd.to_datetime(s.index)
            except: pass
            return s.sort_index().tail(max_quarters)

    return pd.Series(dtype=float)

def _filter_and_add(row, series, metric):
    if series is None or series.empty:
        return
    for dt, val in series.items():
        q = _label_quarter(dt)
        if q in ALLOWED_QUARTERS:
            try:
                row[f"{metric}_{q}"] = float(val)
            except Exception:
                pass

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
            curr_li = _get_series(bal, CURRENT_LIAB)
            curr_as = _get_series(bal, CURRENT_ASSETS)
            tot_debt = _get_series(bal, TOTAL_DEBT)

            # Primary pulls (robust)
            cor      = _get_series_caseflex(inc, COR,       keywords=["cost","revenue","sales","cogs"])
            int_exp  = _get_series_caseflex(inc, INT_EXP,   keywords=["interest","debt"])
            tax_exp  = _get_series_caseflex(inc, TAX_EXP,   keywords=["tax","provision"])
            opex_oth = _get_series_caseflex(inc, OPEX_OTHER,keywords=["operating","expense"])
            capex    = _get_series_caseflex(cf,  CAPEX,     keywords=["capital","property","equipment","purchases","ppe"])

            # Fallbacks:
            # - Interest expense: sometimes found in cashflow descriptions
            if (int_exp is None) or int_exp.empty:
                int_exp = _get_series_caseflex(cf, INT_EXP, keywords=["interest"])

            # - CapEx: try broader keywords if still empty
            if (capex is None) or capex.empty:
                capex = _get_series_caseflex(cf, CAPEX, keywords=["capital","purchases","property","plant","equipment"])

            # - TAX derived fallback: Pretax - NetIncome (approx. provision for income taxes)
            if (tax_exp is None) or tax_exp.empty:
                pretax = _get_series_caseflex(inc, PRETAX, keywords=["before tax","pretax","earnings before tax"])
                net    = _get_series_caseflex(inc, NET_INCOME, keywords=["net income"])
                if pretax is not None and not pretax.empty and net is not None and not net.empty:
                    # Align and derive
                    df_tax = (pretax - net).dropna()
                    try: df_tax.index = pd.to_datetime(df_tax.index)
                    except: pass
                    df_tax = df_tax.sort_index()
                    tax_exp = df_tax.tail(8)

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
                (curr_li, "CurrentLiabilities"),
                (curr_as, "CurrentAssets"),
                (tot_debt, "TotalDebt"),
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
            
            _filter_and_add(row, cor,      "CostOfRevenue")
            _filter_and_add(row, int_exp,  "InterestExpense")
            _filter_and_add(row, tax_exp,  "IncomeTaxExpense")   # may be derived
            _filter_and_add(row, opex_oth, "OtherOperatingExpense")
            _filter_and_add(row, capex,    "CapitalExpenditure")
            
            return row
        except Exception:
            time.sleep(pause)

    return {"OriginalTicker": orig_ticker, "YahooSymbol": ytk}

def save_to_csv(df, output_file):
    """
    Save the DataFrame to a CSV file.
    """
    df.to_csv(output_file, index=False)
    




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
        # Cost of revenue / cost of sales
    COR = [
        "Cost Of Revenue","CostOfRevenue","Cost of Goods Sold","CostOfGoodsSold",
        "Cost Of Goods And Services Sold","CostOfGoodsAndServicesSold",
        "Cost Of Sales","CostOfSales","Cost of Sales","Cost of Revenue"
    ]
    
    # Total interest expense
    INT_EXP = [
        "Interest Expense","InterestExpense","Interest Expense Non Operating","InterestExpenseNonOperating",
        "Total Interest Expense","TotalInterestExpense",
        # extra variants seen in the wild
        "Interest And Debt Expense","InterestAndDebtExpense",
        "Interest And Debt Expense Non Operating","InterestAndDebtExpenseNonOperating",
        "Interest Expense Net","InterestExpenseNet"
    ]
    
    # Income tax expense / provision (expanded)
    TAX_EXP = [
        "Income Tax Expense","IncomeTaxExpense","Provision For Income Taxes","ProvisionForIncomeTaxes",
        "Provision for income taxes","Income Taxes","IncomeTaxes",
        "Income Tax (Benefit) Expense","IncomeTaxExpenseBenefit",
        "Income Tax Provision","IncomeTaxProvision","Provision For Income Tax","ProvisionForIncomeTax",
        "Provision For Income Tax (Benefit)","ProvisionForIncomeTaxBenefit"
    ]
    
    # Other / total operating expenses (Yahoo sometimes uses these for the roll-up)
    OPEX_OTHER = [
        "Operating Expense","OperatingExpense","Operating Expenses","OperatingExpenses",
        "Other Operating Expenses","OtherOperatingExpenses",
        # some tickers expose "Total Operating Expenses"
        "Total Operating Expenses","TotalOperatingExpenses"
    ]
    
    # Capital expenditures (typically reported in cash flow and often negative)
    CAPEX = [
        "Capital Expenditure","CapitalExpenditure","Capital Expenditures","CapitalExpenditures",
        # common cash-flow variants
        "Purchase Of Property And Equipment","PurchaseOfPropertyAndEquipment",
        "Investments In Property Plant And Equipment","InvestmentsInPropertyPlantAndEquipment",
        "Purchase Of Fixed Assets","PurchaseOfFixedAssets",
        "Additions To Property Plant And Equipment","AdditionsToPropertyPlantAndEquipment"
    ]
    
    # ---- For derived tax (fallback): we won't output these, only use them if needed ----
    PRETAX = [
        "Pretax Income","PretaxIncome","Income Before Tax","IncomeBeforeTax",
        "Earnings Before Tax","EarningsBeforeTax","Income Loss Before Income Taxes","IncomeLossBeforeIncomeTaxes"
    ]
    NET_INCOME = [
        "Net Income","NetIncome","Net Income Common Stockholders","NetIncomeCommonStockholders",
        "Net Income Applicable To Common Shares","NetIncomeApplicableToCommonShares"
    ]

    # ---------------- Candidate labels (Balance Sheet only) ----------------
    CURRENT_LIAB = [
        "Total Current Liabilities","TotalCurrentLiabilities",
        "Current Liabilities","CurrentLiabilities", "current liabilities","Current liabilities","Current debt","Current Debt","Deposits"
    ]
    
    
    CURRENT_ASSETS = [
        "Total Current Assets","TotalCurrentAssets",
        "Current Assets","CurrentAssets", "current assets","Current assets","Trading Securities","Trading Assets","Trading securities","Trading assets"
    ]

    CURRENT_LIAB = [
    "Total Current Liabilities","TotalCurrentLiabilities",
    "Current Liabilities","CurrentLiabilities","current liabilities",
    "Current liabilities","Current debt","Current Debt","Deposits"
]

    CURRENT_ASSETS = [
        "Total Current Assets","TotalCurrentAssets",
        "Current Assets","CurrentAssets","current assets",
        "Current assets","Trading Securities","Trading Assets",
        "Trading securities","Trading assets"
    ]
    
    TOTAL_DEBT = [
        "Total Debt","TotalDebt",
        "Short Long Term Debt","Short Long Term Debt Total","Short/Long Term Debt",
        "Long Term Debt","LongTermDebt","Long-term debt","Long Term Debt Noncurrent",
    ]

    # Build allowed quarter labels (exclude current quarter)
    ORDERED_QUARTERS = _last_n_completed_quarters(n=5)  # e.g., ['2025Q2','2025Q1','2024Q4','2024Q3','2024Q2']
    ALLOWED_QUARTERS = set(ORDERED_QUARTERS)

    orig_tickers = build_ticker_mapping(df)
    print(f"\nFound {len(orig_tickers)} unique tickers to process from your original CSV file.\n")
    
    metrics = fetch_metrcis(orig_tickers, max_workers=8)
    print(f"Fetched financial metrics for {len(metrics)} tickers.\n")

    # Merge the dataframes on 'Ticker' and 'OriginalTicker'
    merged_df = pd.merge(df, metrics, left_on='Ticker', right_on='OriginalTicker', how='left')
    print(f"Merged data contains {merged_df.shape[0]} rows and {merged_df.shape[1]} columns.\n")

    # Optional: move identification columns to the front
    id_cols = [c for c in ["Ticker","Name","Sector","OriginalTicker","YahooSymbol", "Weight (%)"] if c in merged_df.columns]
    metric_cols = [c for c in merged_df.columns if c not in id_cols]
    merged_df = merged_df[id_cols + sorted(metric_cols)]
    
    print("Target quarters (most recent first):", ORDERED_QUARTERS)
    print(merged_df.head())

    save_to_csv(merged_df, args.output_file)
    print(f"Data downloaded and saved to {args.output_file}\n")
