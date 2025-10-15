====================================  
Clustering Performance and Forecasting Revenue with Financial and Macroeconomic Data (Q2_2024 – Q2_2025)
====================================

Project Title
--------------
Clustering Performance and Forecasting Revenue with Financial and Macroeconomic Data
(See: `Team10_MilestoneII_Proposal.pdf` For a more comprehensive project outline)

Project Overview
----------------
Our project begins with a .CSV file containing basic stock information for the iShares Russell 3000 ETF which is an exchange traded fund that tracks the investment results of a broad-based index composed of 3000 US equities. The CSV file can be downloaded from the 'ishares' website: https://www.ishares.com/us/products/239714/ishares-russell-3000-etf  

This file is contained in the repository as:
`Russell_3000.csv` and will be the original input file necessary to run our Machine Learning Pipeline. All other files will be built upon this file. However, we have designed this pipeline to be compatible with any ETF CSV file downloaded in a similar fashion.

We have engineered features that allow for a more accurate prediction of the next quarters Revneue which can be used to value a company and help determine potential mid- to long-term investment opportunities.

Raw Data
----------------
We extracted key financial data from yfinance: 

- Ticker: Company Stock Symbol  
- Name: Company Name  
- Sector: Sector Company Belongs to  
- Asset Class: Used to filter out Equities  
- CashAndSTInvestments_XXXXX - Cash And Short Term Investments for YEAR and QUARTER
- CashFromOps_XXXXX - Cash From Operations or Operating Cash Flow for YEAR and QUARTER
- EPS_XXXXX - Net Income and Preferred Dividends/Weighted average shares outstanding for YEAR and QUARTER.
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
Python Files For Pipeline
==================================== 
`data_acquisition.py` 
- Takes the Russell_3000.csv file and uses yfinance to add all quarterly financial statements to the datafile

`data_acquisition_macro.py`
- Adds macro-economic data to the dataset from the St. Louis FED FRED API  

`Clean.py`
- Cleans and removes data that may cause inaccuracies in our modeling

`train_test_split.py`
- Data is split into training and testing sets before any data imputation

`X_train_X_test_filled.py`
- Data is split into subcategories of sector and market cap for imputation of missing values  

`make_KPIs.py`
- Calculating Key Performance Indicators for the financial data to try and pull out nuances of financial data

`make_QoQ.py` 
- Adding temporal relationships by incorporating Quarter-over-Quarter (QoQ) changes and rates of change

`extract_features.py`
- Use unsupervised learning (Principal Component Analysis) to create uncorrelated orthogonal financial features.

`helpers.py`
- Additional helper functions for cleaning and feature engineering

`unsupervised_helpers.py`
- Helper functions for principal component analysis (PCA)

==================================== 
Dataset Checkpoint CSV files
==================================== 
`Russell_3000.csv`
- Initial dataset used to query APIs for financial data

`Russell_3000_Fundamentals.csv`
- All companies from initial dataset with all quarterly financial data obtained from yfinance

`Russell_3000_With_Macro.csv`
- All fundamental data supplemented with macroeconomic data from FRED API

`Russell_3000_Cleaned.csv`
- Russell data cleaned and reformatted for better interpretation in machine learning models  

`X_train.csv, y_train.csv, X_test.csv, y_train.csv`
- Four separate CSV files to avoid data leakage in our machine learning

`X_train_filled.csv, X_test_filled.csv`
- Missing values imputed from sector/market capitalization grouping means

`X_train_filled_KPIs.csv, X_test_filled_KPIs.csv`
- Calculated Key Performance Intervals based on Quarterly financial data  

`X_train_filled_KPIs_QoQ.csv, X_test_filled_KPIs_QoQ.csv`
- Incorporated temporal factors by calculating Quarter over Quarter Ratios  

`X_train_filled_KPIs_QoQ_PCA.csv, X_test_filled_KPIs_QoQ_PCA.csv`
- Principal component analysis features added to dataset for final machine learning model building.

==================================== 
Notebook Files
==================================== 

Thomas' Notebooks
-----------------
`1 - Intro to yfinance.ipynb`
- Introductory notebook to show interaction with the yfinance API. 

`2 - Dealing_With_yfinanance_Throttling.ipynb`
- Rate limiting through yfinance needs to be addressed when querying 2600+ companies

`3 - Macro_Data_Fred.ipynb`
- Introduction to using the FRED API to get Macro Economic data from the St. Louis FED.

`4 - Data_Exploration_Notebook.ipynb`
- Initial jupyter notebook to explore and clean data used to build the clean.py file.

`5 - Train Test Split Notebook.ipynb`
- Setting up custom functions to split our training and testing data based on sector/market capitalization

`6 - Feature_Engineering_PartII.ipynb`
- Calculating Quarter Over Quarter (QoQ) changes and rate changes in the financial data to capture temporal trends. 

`7 - Troubleshooting QoQ Calculations.ipynb`
- Rate calculations have to be robust enough to deal with zero values and infinite values, rate is line of best fit slope  

`8 - t-SNE Exploration and Visualization.ipynb`
- Notebook using unsupervised learning to visualize local structure of 300+ financial feature space

`9 - Baseline Supervised Learning Models.ipynb`
- Notebook used to test baseline model families of supervised learning to narrow down model families best suited to our problem  

`10 - Hyerparameter Turning.ipynb`
- Hyperparameter tuning of our best model family and in-depth evaluation of the champion model including sensitivity analysis, feature importance, feature ablation, failure analysis, and learning curve analysis.

Pete's Noetbooks
----------------
`clean.ipynb`
-

`Initial_Analysis_09-18.ipynb`
- 

`K-Means_log-transform.ipynb`
-

`K-Means_quantile-scaler.ipynb`
-

`K-Means.ipynb`
-

`Log_transform.ipynb`
-

`make_KPIs.ipynb`
-

`PCA_log-transform.ipynb`
-

`PCA_pipeline.ipynb`
-

`PCA_quantile-scaler.ipynb`
-

`PCA.ipynb`
-

1Supplemental_Data_Exploration.ipynb`
- 

Melody's Notebooks
------------------
`Missing_value_fillin.ipynb`
-

`MLP_1008.ipynb`
-


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

### In Ubunto Terminal run Makefile with
```
$ make
```

---

## Notes

- Use **`environment.yml`** for Conda workflows.  
- Use **`requirements.txt`** for pip workflows.  
- After installing new packages, always re-export (`conda env export` or `pip freeze`) to keep these files current.
