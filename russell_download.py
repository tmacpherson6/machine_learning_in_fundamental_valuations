'''
This is going to be the first file in the pipeline for our dataset creation and preparation for the machine learning model.

It will download the data from the given URL and update with additional financial data.

The output will be a csv file that will be used in the next step of the pipeline.
'''
import pandas as pd


def download_russell_3000_data(output_file: str) -> None:
    """
    Downloads the Russell 3000 ETF data from the given URL and saves it as a CSV file.

    Parameters:
    url (str): The URL to download the data from.
    output_file (str): The path to save the downloaded CSV file.
    """
    url =  'https://www.ishares.com/us/products/239714/ishares-russell-3000-etf/1521942788811.ajax?fileType=xls&fileName=iShares-Russell-3000-ETF_fund&dataType=fund'
    df = pd.read_excel(url, skiprows=0)


if __name__ == "__main__":
    output_file = 'Russell_3000.csv'
    download_russell_3000_data(output_file)
    print(f"Data downloaded and saved to {output_file}")