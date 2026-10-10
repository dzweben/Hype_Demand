import os

#%%
# ...existing code...

import requests
import pandas as pd

# Initialize REDCap project
api_url = "https://cphapps.temple.edu/redcap/api/"
api_token = os.environ["REDCAP_API_TOKEN"]

# Function to download REDCap report data
def download_redcap_report(api_url, api_token, report_id):
    data = {
        'token': api_token,
        'content': 'report',
        'format': 'json',
        'report_id': report_id,
        'rawOrLabel': 'raw',
        'rawOrLabelHeaders': 'raw',
        'exportCheckboxLabel': 'false',
        'returnFormat': 'json'
    }
    response = requests.post(api_url, data=data)
    response.raise_for_status()  # Raise an error for bad status codes
    return pd.DataFrame(response.json())

# Download the reports as DataFrames
sys_reverse_1stHDTDocOnly = download_redcap_report(api_url, api_token, '8225')
sys_reverse_1stHDTNonDocOnly = download_redcap_report(api_url, api_token, '8226')
sys_reverse_2ndHDTDocOnly = download_redcap_report(api_url, api_token, '8229')
sys_reverse_2ndHDTNonDocOnly = download_redcap_report(api_url, api_token, '8228')

# Display the DataFrames to ensure they are loaded correctly
print(sys_reverse_1stHDTDocOnly.head())
print(sys_reverse_1stHDTNonDocOnly.head())
print(sys_reverse_2ndHDTDocOnly.head())
print(sys_reverse_2ndHDTNonDocOnly.head())

# ...existing code...
# %%
# Function to perform 10 - value for all numeric columns except 'record_id'
def subtract_from_ten(df):
    # Convert all columns to numeric, forcing errors to NaN
    df = df.apply(pd.to_numeric, errors='coerce')
    
    # Select numeric columns except 'record_id'
    numeric_cols = df.select_dtypes(include='number').columns
    if 'record_id' in numeric_cols:
        numeric_cols = numeric_cols.drop('record_id')
    
    # Perform the 10 - operation on numeric columns
    df[numeric_cols] = 10 - df[numeric_cols]
    return df

# Apply the function to each DataFrame
sys_reverse_1stHDTDocOnly = subtract_from_ten(sys_reverse_1stHDTDocOnly)
sys_reverse_1stHDTNonDocOnly = subtract_from_ten(sys_reverse_1stHDTNonDocOnly)
sys_reverse_2ndHDTDocOnly = subtract_from_ten(sys_reverse_2ndHDTDocOnly)
sys_reverse_2ndHDTNonDocOnly = subtract_from_ten(sys_reverse_2ndHDTNonDocOnly)


# %%


### CHECK FOR MATCH

# Check if the DataFrames match the corresponding CSV files
def check_dataframe_match(df, csv_path):
    csv_df = pd.read_csv(csv_path)
    return df.equals(csv_df)

# Paths to the CSV files
csv_paths = [
    "/Users/dannyzweben/Desktop/KylerDissAccessSanityChecks/sys_reverse_1stHDTDocOnly.csv",
    "/Users/dannyzweben/Desktop/KylerDissAccessSanityChecks/sys_reverse_1stHDTNonDocOnly.csv",
    "/Users/dannyzweben/Desktop/KylerDissAccessSanityChecks/sys_reverse_2ndHDTDocOnly.csv",
    "/Users/dannyzweben/Desktop/KylerDissAccessSanityChecks/sys_reverse_2ndHDTNonDocOnly.csv"
]

# Check each DataFrame against its corresponding CSV file
matches = [
    check_dataframe_match(sys_reverse_1stHDTDocOnly, csv_paths[0]),
    check_dataframe_match(sys_reverse_1stHDTNonDocOnly, csv_paths[1]),
    check_dataframe_match(sys_reverse_2ndHDTDocOnly, csv_paths[2]),
    check_dataframe_match(sys_reverse_2ndHDTNonDocOnly, csv_paths[3])
]

# Print the results
for i, match in enumerate(matches):
    print(f"DataFrame {i+1} matches CSV: {match}")
# %%
### Kyler's data was scored and cleaned correctly. 
