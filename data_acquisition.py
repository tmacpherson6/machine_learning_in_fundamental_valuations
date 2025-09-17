'''
This is going to be the first file in the pipeline for our dataset creation and preparation for the machine learning model.

It will load the Russell 3000 data and update with additional financial data.

The output will be a csv file that will be used in the next step of the pipeline.
'''

import pandas as pd


def download_russell_3000_data(input_file: str, output_file: str) -> None:
    """
    Downloads the Russell 3000 ETF data from the Repo, updates the data, and saves it as a new checkpoint CSV file.

    Parameters:
    input_file (str): The original Russell 3000 CSV file path.
    output_file (str): The path to save the downloaded CSV file.
    """
    # Load the Russell 3000 data from the provided CSV file
    df = pd.read_csv(input_file)
    
    # Perform any necessary data updates here
    
    
    # Save the updated DataFrame to a new CSV file
    #df.to_csv(output_file, index=False)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help = 'Title of input file: Russell_3000.csv')
    parser.add_argument('output_file', help = 'Title of output file. ')
    args.parser.parse_args()

    # Set the output file name and export the data
    input_file = args.input_file
    download_russell_3000_data(input_file, output_file)
    # Screen logging on the completion of the download
    print(f"Data downloaded and saved to {output_file}")
    