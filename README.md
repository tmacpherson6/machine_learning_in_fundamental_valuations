====================================  
Corporate Valuation using Quarterly Finanical Data and Machine Learning (Q2_2024 – Q2_2025)
====================================

Project Title
--------------
Predicting Earnings and Clustering Performance with Financial and Macroeconomic Data
(See: `Team10_MilestoneII_Proposal.pdf` For a more comprehensive project outline)

Project Overview
----------------
Our project begins with a .CSV file containing basic stock information for the iShares Russell 3000 ETF which is an exchange traded fund that tracks the investment results of a broad-based index composed of 3000 US equities. The CSV file can be downloaded from the 'ishares' website: https://www.ishares.com/us/products/239714/ishares-russell-3000-etf  

This file is contained in the repository as:
`Russell_3000.csv` and will be the original input file necessary to run our Machine Learning Pipeline. All other files will be built upon this file. However, we have designed this pipeline to be compatible with any ETF CSV file downloaded in a similar fashion.

We have engineered features that allow for a more accurate prediction of the next quarters Earnings-per-share which can be used to value a company and help determine potential mid- to long-term investment opportunities.

Raw Data
----------------
We extracted key financial data from yfinance: 

- Ticker: Company Stock Symbol  
- Name: Company Name  
- Sector: Sector Company Belongs to  
- Asset Class: Used to filter out Equities  
- CashAndSTInvestments_XXXXX - Cash And Short Term Investments for YEAR and QUARTER
- CashFromOps_XXXXX - Cash From Operations or Operating Cash Flow for YEAR and QUARTER
- EPS_XXXXX - TARGET VARIABLE - Net Income and Preferred Dividends/Weighted average shares outstanding for YEAR and QUARTER.
- Exchange - Exchange the security is traded on  
- Location - Country of Buisness HeadQuarters  
- LongTermDebt_XXXXXX - Long Term Debt for YEAR and QUARTER  
- Market Value - Total Market Value of Company (Market Cap) in quantitative value (x1000) 
- NetIncome_XXXXXX - Revenue - (Operating expenses + Interest + taxes + other expenses) for YEAR and QUARTER  
- Notional Value - For equities this is Share Price x Number of Shares (different if it were for derivatives)  
- OperatingIncome_XXXXXX - Revenue - Operating Expenses for YEAR and QUARTER
- Price - Recent Stock Price at time of data acquisition ($)
- Quantity - Current outstanding shares (x1000)
- Revenue_XXXXXX - Total Revenue for YEAR and QUARTER  
- ShortTermDebtOrCurrentLiab_XXXXXX - Short term debt and current liabilities for YEAR and QUARTER  
- TotalAssets_XXXXX - Total Assets for YEAR and QUARTER  
- TotalEquity_XXXXX - Total shareholders equity for YEAR and QUARTER  
- TotalLiabilities_XXXXXX - Total liabilities for YEAR and QUARTER  
- Weight (%) - Percent Weight in the Russell 3000 Index  
- CapitalExpenditure_XXXXXX - Money spent to acquire, upgrade or maintain long-term assets (CAPEX) for YEAR and QUARTER
- CostOfRevenue_XXXXXX- Similar to Cost of goods sold (COGS) but includes cost of delivery and product/services for YEAR and QUARTER  
- IncomeTaxExpense_XXXXXX - Taxable income X Effective Tax Rate for YEAR and QUARTER  
- InterestExpense_XXXXXX - Cost of borrowing money (bonds, bank loans, credit lines) for YEAR and QUARTER  
- OtherOperatingExpense_XXXXX - Any Other Operating expenses in YEAR and QUARTER

Feature Engineering
----------------
- <RawFeature>_QoQ_YYQQ_YYQQ - We took the quarter over quarter change in all financial features in order to capture some temporal structure. The feature column is in the format of the rawfeaturename_QoQ_YearQuarter_YearQuarter where it is the change between the two quarters named.  
- <RawFeature>_QoQ_Rate - We took the slope of the OLS linear regression of the quarterly rate change datapoints to get a rate change over all of the historical quarters that we have.  
- KPI_GrossProfitMargin - (Revenue - Cost of Sales) / Revenue
- KPI_NetProfitMargin - Net Profit / Revenue
- KPI_Leverage - Total Assets / Total Equity
- KPI_DebtToEquityRatio - Total Debt / Total Equity  
- KPI_TotalAssetTurnover - Revenue / Average Total Assets
- KPI_ReturnOnEquity - Net Profit / Average Equity
- KPI_ReturnOnAssets - Net Profit / Average Total Assets

==================================== 
Python Files 
==================================== 


==================================== 
Notebook Files
==================================== 
`Tom's_Data_Exploration_Notebook.ipynb`
- Initial jupyter notebook to explore and clean data used to build the cleaning.py file.

`Feature_Engineering_PartII.ipynb`
- Calculating Quarter Over Quarter (QoQ) changes and rate changes in the financial data to capture temporal trends. 




*Additional project documentation will be added as files are created.

==================================== 
Virtual Environment, Makefile and Dependency Setup
==================================== 

This section explains how to create, load, and update environments using both **Conda** and **pip**. 

---

## Using Conda

### Create and Activate Environment
```bash
conda create -n milestoneII python=3.11
conda activate milestoneII
```

### Install Environment and Dependencies from File (PREFERED)
```bash
conda env create -f environment.yml
```

### Update Environment
```bash
conda env update -f environment.yml --prune
```

### Export Dependencies
If you add or remove packages and need to update the `.yml` file:
```bash
conda env export > environment.yml
```

---

## Using pip (venv or virtualenv)

### Create and Activate Environment
**Linux/macOS**
```bash
python3 -m venv milestoneII
source milestoneII/bin/activate
```

**Windows**
```bash
python -m venv milestoneII
milestoneII\Scripts\activate
```

### Install Dependencies from File
```bash
pip install -r requirements.txt
```

### Update Dependencies
```bash
pip install -U -r requirements.txt
```

### Export Dependencies
If you add or remove packages and need to update the `requirements.txt` file:
```bash
pip freeze > requirements.txt
```

### Install WSL (Linux Tools on Windows) for Makefile to work properly
```bash
wsl --install -d Ubuntu
# reopen IDE in WSL then:  
sudo apt update
sudo apt install make
sudo apt install -y python3-venv python3-pip
make --version
```
---

## Notes

- Use **`environment.yml`** for Conda workflows.  
- Use **`requirements.txt`** for pip workflows.  
- After installing new packages, always re-export (`conda env export` or `pip freeze`) to keep these files current.
