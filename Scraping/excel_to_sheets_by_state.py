import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys

# Add the directory containing us_state_abbrev.py to the path
sys.path.append('/Users/dannyzweben/Desktop/CAADC')
from us_state_abbrev import us_state_abbrev  # Dictionary for state abbreviations

# Step 1: Load and Process Excel File
def load_and_process_excel(file_path):
    # Read the Excel file
    df = pd.read_excel(file_path)
    
    # Debugging: Print column names for verification
    print("Columns in the Excel file:", df.columns.tolist())
    
    # Normalize column names and select relevant columns
    df.columns = df.columns.str.strip()
    df = df[['Name', 'Email', 'State']]  # Adjusted to the new column order
    
    # Map state names to abbreviations
    df['State'] = df['State'].map(us_state_abbrev).fillna(df['State'])  # Preserve existing abbreviations
    
    # Handle missing values
    df = df.dropna(subset=['Name', 'Email'])  # Drop rows with missing critical fields
    df = df.fillna('')  # Replace remaining NaN values with empty strings
    
    # Trim whitespace in data
    df['Name'] = df['Name'].str.strip()
    df['Email'] = df['Email'].str.strip()
    df['State'] = df['State'].str.strip()
    
    # Return processed DataFrame
    return df

# Step 2: Authenticate with Google Sheets
def authenticate_google_sheets(credentials_file, sheet_name):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name)

# Step 3: Update Sheets by State with Correct Column Order
def update_google_sheets_by_state(workbook, data_frame):
    for state, group in data_frame.groupby('State'):
        try:
            # Get the worksheet for the state
            worksheet = workbook.worksheet(state)
            
            # Fetch existing names in the sheet
            existing_names = set(row[0] for row in worksheet.get_all_values()[1:])  # Skip the header row
            
            # Filter rows where the name does not already exist
            filtered_group = group[~group['Name'].isin(existing_names)]
            
            if not filtered_group.empty:
                # Ensure columns are in the correct order: Name, Email, State
                data_to_append = filtered_group[['Name', 'Email', 'State']]  # Adjusted to match your new order

                # Print the data being appended for debugging
                print(f"\nAppending data to sheet {state}:")
                print(data_to_append.head())

                # Append rows
                worksheet.append_rows(
                    data_to_append.values.tolist(),
                    table_range="A1"
                )
                print(f"Updated sheet for {state} with {len(data_to_append)} new rows.")
            else:
                print(f"No new rows to update for {state}.")
        except gspread.exceptions.WorksheetNotFound:
            print(f"Sheet for {state} not found. Skipping.")

# Main function
def main():
    # File paths and Google Sheets information
    excel_file_path = "/Users/dannyzweben/Desktop/CAADC/DATA_by_zipcodes.xlsx"
    credentials_file = "/Users/dannyzweben/Desktop/CAADC/arcane-boulder-445318-e0-ae3efe15a20e.json"
    google_sheet_name = "APA Psychologist Locator Scraping"

    # Load and process data
    data = load_and_process_excel(excel_file_path)

    # Authenticate and get Google Sheets workbook
    workbook = authenticate_google_sheets(credentials_file, google_sheet_name)

    # Update each sheet by state
    update_google_sheets_by_state(workbook, data)

    print("\nData transfer complete!")

if __name__ == "__main__":
    main()
