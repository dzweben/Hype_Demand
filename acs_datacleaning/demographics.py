# %%

import pandas as pd
import numpy as np
import os

# Remove specified record ids from all subsequent tables
drop_ids = [241, 409, 491]

# Helper function to drop these IDs from any DataFrame
def drop_excluded_ids(df):
    return df[~df['record_id'].isin(drop_ids)]

# Load the CSV file into a DataFrame (demographics, criteria ranking, screening )
rawdata = pd.read_csv("/Users/dannyzweben/Desktop/CAADC/acs_datacleaning/access-demo.ranking..csv")

#%%
# Load the CSV file into a DataFrame (exlusion? )
usabledata = pd.read_csv("/Users/dannyzweben/Desktop/CAADC/acs_datacleaning/usable-data-report.csv")

# Create 'exclusionstatus' column
usabledata['exclusionstatus'] = np.select(
    condlist=[
        usabledata['fraudulent'] == 1,
        usabledata['unverified'] == 1,
        usabledata['accepts_medicade'] == 1
    ],
    choicelist=['fraudulent', 'unverified', 'accepts >50% medicare'],
    default='include'  # Default is 'include' when no other conditions are met
)

usabledatacomplete = usabledata[['record_id', 'exclusionstatus']]


# %%
# merge the data frames
rawdata.rename(columns={"Record ID": "record_id"}, inplace=True)
df1 = pd.merge(rawdata, usabledatacomplete, on='record_id', how='inner')


# %%
##add HDT completion and merge

hdtcomplete = pd.read_csv("/Users/dannyzweben/Desktop/CAADC/acs_datacleaning/hdt-completion.csv")
df1 = pd.merge(df1, hdtcomplete, on='record_id', how='inner')

# %%
#### next tasks: 
# create a total complete (hdt, crr =2, and inclusion status, and demographic report)
# create seperate dfs for crr = 2, and for hdt = 2

### create seperate df externally to track the following status: 
    #    (from usable data)
    #    incomplete (no usable data)
    #    cr complete
    #    hdt complete 
    #    Briana complete
    #    Margerate complete

    #    fraudenlent
    #    unverified
    #    >50 % medicare


## create a cool table: partial data, complete data, unusable data
##cchecking progress
df1.to_csv("/Users/dannyzweben/Desktop/CAADC/acs_datacleaning/progress.csv", index=False)

#%%
#completion report df building:

df1.rename(columns={"Complete?": "cr_complete", "hypothetical_demand_task_complete": "hdt_complete"}, inplace=True)
df1["hdt_complete"] = df1["hdt_complete"].replace({2: "Complete", 0: "Incomplete"})
df1_cr = df1[["record_id", "cr_complete", "hdt_complete", "exclusionstatus"]]

# %%
from redcap import Project
import pandas as pd

# Initialize REDCap project
api_url = "https://cphapps.temple.edu/redcap/api/"
api_token = "REMOVED"
project = Project(api_url, api_token)

# Pull data for specific fields (record_id, briana_complete, margaret_complete)
fields = ["record_id", "briana_complete", "margaret_complete"]
data = project.export_records(fields=fields, format_type="json")

# Convert the JSON data to a pandas DataFrame
data_df = pd.DataFrame(data)

# Explicitly copy df1_cr to avoid SettingWithCopyWarning
df1_cr = df1_cr.copy()

# Ensure 'record_id' in both DataFrames is the same type (e.g., string)
df1_cr["record_id"] = df1_cr["record_id"].astype(str)
data_df["record_id"] = data_df["record_id"].astype(str)

# Merge the REDCap data with df1_cr on the record_id column
df1_cr = df1_cr.merge(data_df, on="record_id", how="left")

# %%
#### double checking medicare number:
from redcap import Project
import pandas as pd

# Initialize REDCap project
api_url = "https://cphapps.temple.edu/redcap/api/"
api_token = "REMOVED"
project = Project(api_url, api_token)

# Pull data for specific fields (record_id, accepted_insurance_plans, medicare_population)
fields = ["record_id", "accepted_insurance_plans", "medicare_population"]
data = project.export_records(fields=fields, format_type="json")

# Convert the JSON data to a pandas DataFrame
medicare_check_df = pd.DataFrame(data)

# Display the data
print(medicare_check_df)
medicare_check_df.to_csv("medicare_check_data.csv", index=False)

# %%
df1_cr["briana_complete"] = pd.to_numeric(df1_cr["briana_complete"], errors="coerce")
df1_cr["margaret_complete"] = pd.to_numeric(df1_cr["margaret_complete"], errors="coerce")

# Replace the values 2 with "Complete" and 0 with "Incomplete"
df1_cr["briana_complete"] = df1_cr["briana_complete"].replace({2: "Complete", 0: "Incomplete"})
df1_cr["margaret_complete"] = df1_cr["margaret_complete"].replace({2: "Complete", 0: "Incomplete"})

# %%

### list of partial completion!
##CR
## HDT: 164, 223, 272, 277, 306, 329, 330, 372, 399, 632, 639, 671, 859, 878, 
# Define the record_id values for which hdt_complete should be changed
partial_ids = [164, 223, 272, 277, 306, 329, 330, 372, 399, 632, 639, 671, 859, 878]

# Update hdt_complete to "Partial" for the specified record_id values
df1_cr.loc[df1_cr["record_id"].astype(int).isin(partial_ids), "hdt_complete"] = "Partial"

##Briana partial: 880
df1_cr['record_id'] = df1_cr['record_id'].astype(int)
df1_cr.loc[df1_cr['record_id'] == 880, 'briana_complete'] = 'Partial'


# %%
df1_cr.rename(columns={
    'margaret_complete': 'margaret',
    'briana_complete': 'briana',
    'hdt_complete': 'hypothetical demand dask',
    'cr_complete': 'criteria ranking'
}, inplace=True)

# %%
# Import pandas
import pandas as pd

# Assuming df1_cr is your DataFrame (already loaded in your script)
#### RIGHT HERE --> MIGHT MANUALLY APPLY BRANCHING LOGIC!
import numpy as np
### removing medicare record ids for clinicians who accepted medicare.

# List of record IDs
record_ids = [54, 47, 57, 43, 60]

# List of columns to be updated
columns_to_update = [
    'Reimbursement rates are too low',
    'Administrative burden of submitting claims',
    'Delays in getting paid',
    'Concerns about treatment regulations',
    'Concerns about audit risk',
    'Not accepted onto an insurance panel',
    'Do you have any other reasons not listed above? If so, please include your reason and where it would fall on the ranking here:'
]

# Update the specified columns for the specified record IDs
df1.loc[df1['record_id'].isin(record_ids), columns_to_update] = np.nan
#%%
#### remove medicaid record ids for clinicians who accepted medicaid. 
# List of record IDs
record_ids = [9, 140, 43, 186]

# List of columns to be updated
columns_to_update = [
    'Reimbursement rates are too low.1',
    'Administrative burden of submitting claims.1',
    'Delays in getting paid.1',
    'Concerns about treatment regulations.1',
    'Concerns about audit risk.1',
    'Not accepted onto an insurance panel.1',
    'Do you have any other reasons not listed above? If so, please include your reason and where it would fall on the ranking here:.1'
]

# Update the specified columns for the specified record IDs
df1.loc[df1['record_id'].isin(record_ids), columns_to_update] = np.nan

#%% ### Checking if this worked - It did. 

# Print the value for the specified column and record ID
print(df1.loc[df1['record_id'] == 54, 'Reimbursement rates are too low'].values[0])
print(df1.loc[df1['record_id'] == 47, 'Reimbursement rates are too low'].values[0])
print(df1.loc[df1['record_id'] == 9, 'Reimbursement rates are too low.1'].values[0])


#%%

# Calculate counts for Hypothetical Demand Task
hdt_complete_count = df1_cr[
    (df1_cr["hypothetical demand dask"] == "Complete") & 
    (df1_cr["exclusionstatus"] == "include")
].shape[0]

hdt_partial_count = df1_cr[
    (df1_cr["hypothetical demand dask"] == "Partial") & 
    (df1_cr["exclusionstatus"] == "include")
].shape[0]

# Calculate counts for Margaret
margaret_complete_count = df1_cr[
    (df1_cr["margaret"] == "Complete") & 
    (df1_cr["exclusionstatus"] == "include")
].shape[0]

margaret_partial_count = df1_cr[
    (df1_cr["margaret"] == "Partial") & 
    (df1_cr["exclusionstatus"] == "include")
].shape[0]

# Calculate counts for Brianna
brianna_complete_count = df1_cr[
    (df1_cr["briana"] == "Complete") & 
    (df1_cr["exclusionstatus"] == "include")
].shape[0]

brianna_partial_count = df1_cr[
    (df1_cr["briana"] == "Partial") & 
    (df1_cr["exclusionstatus"] == "include")
].shape[0]

# Calculate counts for Criteria Ranking
criteria_complete_count = df1_cr[
    (df1_cr["criteria ranking"] == "Complete") & 
    (df1_cr["exclusionstatus"] == "include")
].shape[0]

criteria_partial_count = df1_cr[
    (df1_cr["criteria ranking"] == "Partial") & 
    (df1_cr["exclusionstatus"] == "include")
].shape[0]

## add medicare
# Calculate counts for Criteria Ranking with additional condition
medicare_criteria_complete_count = df1_cr[
    (df1_cr["criteria ranking"] == "Complete") & 
    (df1_cr["exclusionstatus"] == "include") & 
    (df1["Reimbursement rates are too low"].notna()) & 
    (df1["Reimbursement rates are too low"] != "")
].shape[0]

medicare_criteria_partial_count = df1_cr[
    (df1_cr["criteria ranking"] == "Partial") & 
    (df1_cr["exclusionstatus"] == "include") & 
    (df1["Reimbursement rates are too low"].notna()) & 
    (df1["Reimbursement rates are too low"] != "")
].shape[0]

## add medicade
# Calculate counts for Criteria Ranking with additional condition
medicaid_criteria_complete_count = df1_cr[
    (df1_cr["criteria ranking"] == "Complete") & 
    (df1_cr["exclusionstatus"] == "include") & 
    (df1["Reimbursement rates are too low.1"].notna()) & 
    (df1["Reimbursement rates are too low.1"] != "")
].shape[0]

medicaid_criteria_partial_count = df1_cr[
    (df1_cr["criteria ranking"] == "Partial") & 
    (df1_cr["exclusionstatus"] == "include") & 
    (df1["Reimbursement rates are too low.1"].notna()) & 
    (df1["Reimbursement rates are too low.1"] != "")
].shape[0]

#### add Private Insruance?

# Calculate counts for Criteria Ranking with additional condition
private_criteria_complete_count = df1_cr[
    (df1_cr["criteria ranking"] == "Complete") & 
    (df1_cr["exclusionstatus"] == "include") & 
    (df1["Reimbursement rates are too low.2"].notna()) & 
    (df1["Reimbursement rates are too low.2"] != "")
].shape[0]

private_criteria_partial_count = df1_cr[
    (df1_cr["criteria ranking"] == "Partial") & 
    (df1_cr["exclusionstatus"] == "include") & 
    (df1["Reimbursement rates are too low.2"].notna()) & 
    (df1["Reimbursement rates are too low.2"] != "")
].shape[0]

# Combine all results into a table
results_table = pd.DataFrame({
    "Survey": ["Hypothetical Demand Task", "Margaret", "Briana", "Criteria Ranking", "Medicare", "Medicaid", "Private"],
    "Complete": [hdt_complete_count, margaret_complete_count, brianna_complete_count, criteria_complete_count,medicare_criteria_complete_count, medicaid_criteria_complete_count, private_criteria_complete_count ],
    "Partial": [hdt_partial_count, margaret_partial_count, brianna_partial_count, criteria_partial_count, medicare_criteria_partial_count, medicaid_criteria_partial_count, private_criteria_partial_count ]
})

# Display the table
# Optionally, save the table to a CSV file
results_table.to_csv("survey_completion_table.csv", index=False)

###medicare ## double check
print("Number of people meeting the criteria:", df1_cr[
    (df1_cr["criteria ranking"] == "Complete") & 
    (df1_cr["exclusionstatus"] == "include") & 
    (medicare_check_df["accepted_insurance_plans___3"] == '0') & 
    (medicare_check_df["medicare_population"] == '1')
].shape[0])

#%%
### people who completed criteria ranking but stopped during demographics

# Calculate and print the count for criteria ranking "Complete" with exclusion status "unverified"
criteria_partial_count = df1_cr[
    (df1_cr["criteria ranking"] == "Complete") & 
    (df1_cr["exclusionstatus"] == "unverified")
].shape[0]

print(criteria_partial_count)

#### came out to 74. 


# %%
from docx import Document
import pandas as pd

# Assuming 'results_table' is your DataFrame
# Example DataFrame (replace with your actual 'results_table')
data = {
    "Survey": ["Hypothetical Demand Task", "Margaret", "Briana", "Criteria Ranking"],
    "Complete": [309, 306, 306, 329],
    "Partial": [14, 0, 1, 0]
}
results_table = pd.DataFrame(data)

# Create a new Word document
doc = Document()

# Add a title for the table
doc.add_heading("Usable Data", level=2)

# Add the table to the Word document
table = doc.add_table(results_table.shape[0] + 1, results_table.shape[1])
table.style = "Table Grid"

# Add column headers
for col_num, col_name in enumerate(results_table.columns):
    table.cell(0, col_num).text = col_name

# Add the data rows
for row_num, row in results_table.iterrows():
    for col_num, value in enumerate(row):
        table.cell(row_num + 1, col_num).text = str(value)

# Save the Word document
try:
    doc.save("/Users/dannyzweben/Desktop/CAADC/acs_datacleaning/Usable_Data.docx")
    print("Word document 'Usable_Data.docx' has been created and saved successfully!")
except Exception as e:
    print(f"Error saving Usable_Data.docx: {e}")


##### Seperate CR completion numbers (medicaire, mediacid, private, added to this table 
##### by hand from the CSV generated above)
# %%

import pandas as pd

# Assuming df1_cr is your DataFrame

# Calculate the values for the "Sample" column based on exclusionstatus
usable_data_count = df1_cr[df1_cr["exclusionstatus"] == "include"].shape[0]
unverified_therapist_info_count = df1_cr[df1_cr["exclusionstatus"] == "unverified"].shape[0]
accepts_medicare_count = df1_cr[df1_cr["exclusionstatus"] == "accepts >50% medicare"].shape[0]
fraudulent_count = df1_cr[df1_cr["exclusionstatus"] == "fraudulent"].shape[0]

# Calculate "Ineligible/Incomplete"
ineligible_incomplete_count = df1_cr[
    (df1_cr["exclusionstatus"] == "include") & 
    (df1_cr["criteria ranking"] == "Incomplete") &
    (df1_cr["hypothetical demand dask"] == "Incomplete") &
    (df1_cr["briana"] == "Incomplete") &
    (df1_cr["margaret"] == "Incomplete")
].shape[0]

# Adjust usable data count to exclude Ineligible/Incomplete
adjusted_usable_data_count = usable_data_count - ineligible_incomplete_count

# Create the new results table
ud_results_table = pd.DataFrame({
    "Status": ["Usable Data", "Unverified Therapist Information", "Accepts >50% Medicare", "Fraudulent", "Ineligible/Incomplete"],
    "Sample": [adjusted_usable_data_count, unverified_therapist_info_count, accepts_medicare_count, fraudulent_count, ineligible_incomplete_count]
})

# Display the table
print(ud_results_table)

# Optionally, save the table to a CSV file
ud_results_table.to_csv("ud_results_table.csv", index=False)

# %%
# Export to a Word document
print(f"Current working directory: {os.getcwd()}")
doc = Document()
doc.add_heading("Completion Summary", level=2)
table = doc.add_table(ud_results_table.shape[0] + 1, ud_results_table.shape[1])
table.style = "Table Grid"
for col_num, col_name in enumerate(ud_results_table.columns):
    table.cell(0, col_num).text = col_name
for row_num, row in ud_results_table.iterrows():
    for col_num, value in enumerate(row):
        table.cell(row_num + 1, col_num).text = str(value)
try:
    doc.save("/Users/dannyzweben/Desktop/CAADC/acs_datacleaning/Completion_Summary.docx")
    print("Word document 'Completion_Summary.docx' has been created and saved successfully!")
except Exception as e:
    print(f"Error saving Completion_Summary.docx: {e}")

# %%
#criteria ranking df
columns_to_select = [
    'record_id', 
    'Reimbursement rates are too low', 'Administrative burden of submitting claims', 'Delays in getting paid',
    'Concerns about treatment regulations', 'Concerns about audit risk', 'Not accepted onto an insurance panel',
    'Do you have any other reasons not listed above? If so, please include your reason and where it would fall on the ranking here:',
    'Reimbursement rates are too low.1', 'Administrative burden of submitting claims.1', 'Delays in getting paid.1',
    'Concerns about treatment regulations.1', 'Concerns about audit risk.1', 'Not accepted onto an insurance panel.1',
    'Do you have any other reasons not listed above? If so, please include your reason and where it would fall on the ranking here:.1',
    'Reimbursement rates are too low.2', 'Administrative burden of submitting claims.2', 'Delays in getting paid.2',
    'Concerns about treatment regulations.2', 'Concerns about audit risk.2', 'Not accepted onto an insurance panel.2',
    'Do you have any other reasons not listed above? If so, please include your reason and where it would fall on the ranking here:.2',
    'Complete?'
]

# Use set intersection to dynamically filter columns in df1
existing_columns = [col for col in columns_to_select if col in df1.columns]
df_cr_data = df1.loc[df1['exclusionstatus'] == 'include', existing_columns]


# %%
### DECISIONS NOT TO ACCEPT MEDICARE: 
#Reimbursement rates are too low	Administrative burden of submitting claims	Delays in getting paid	Concerns about treatment regulations	Concerns about audit risk	Not accepted onto an insurance panel


from docx import Document
import pandas as pd

# Assuming df_cr_data is your DataFrame

# Calculate mean, median, and mode for each reason
stats = df_cr_data[
    [
        "Reimbursement rates are too low", 
        "Administrative burden of submitting claims", 
        "Delays in getting paid", 
        "Concerns about treatment regulations", 
        "Concerns about audit risk", 
        "Not accepted onto an insurance panel"
    ]
].agg(["mean", "median", lambda x: x.mode().iloc[0]])  # Get the mode's first value

# Rename the lambda function column
stats.rename(index={"<lambda_0>": "mode"}, inplace=True)

# Transpose the table for readability
cr_medicare_stats_table = stats.T.reset_index()
cr_medicare_stats_table.columns = ["Reason", "Mean Ranking", "Median Ranking", "Most Common Ranking"]

cr_medicare_stats_table["Mean Ranking"] = cr_medicare_stats_table["Mean Ranking"].round(2)

# Save the table to a Word document
doc = Document()
doc.add_heading("Rankings of Reasons for Not Accepting Medicare", level=2)

# Add the table to the Word document
table = doc.add_table(cr_medicare_stats_table.shape[0] + 1, cr_medicare_stats_table.shape[1])
table.style = "Table Grid"

# Add column headers
for col_num, col_name in enumerate(cr_medicare_stats_table.columns):
    table.cell(0, col_num).text = col_name

# Add the data rows
for row_num, row in cr_medicare_stats_table.iterrows():
    for col_num, value in enumerate(row):
        table.cell(row_num + 1, col_num).text = str(value)

# Save the Word document
try:
    doc.save("/Users/dannyzweben/Desktop/CAADC/acs_datacleaning/cr_medicare_stats_table.docx")
    print("Word document 'cr_medicare_stats_table.docx' has been created and saved successfully!")
except Exception as e:
    print(f"Error saving cr_medicare_stats_table.docx: {e}")

# %%
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

# Custom order for the x-axis with added line breaks for long labels
x_order = [
    "Reimbursement rates\nare too low",
    "Administrative burden\nof submitting claims",
    "Delays in\ngetting paid",
    "Concerns about\ntreatment regulations",
    "Concerns about\naudit risk",
    "Not accepted onto\nan insurance panel"
]

# Ensure cr_medicare_stats_table is sorted in this order
cr_medicare_stats_table = cr_medicare_stats_table.set_index("Reason").reindex(
    [
        "Reimbursement rates are too low",
        "Administrative burden of submitting claims",
        "Delays in getting paid",
        "Concerns about treatment regulations",
        "Concerns about audit risk",
        "Not accepted onto an insurance panel"
    ]
).reset_index()

# Data for the chart
x = np.arange(len(x_order))  # X-axis positions
mean_ranking = cr_medicare_stats_table["Mean Ranking"]
most_common_ranking = cr_medicare_stats_table["Most Common Ranking"]

# Plot grouped horizontal bars
plt.figure(figsize=(12, 8))  # Increased figure size for better readability
bar_width = 0.4

# Set the font to Times New Roman
mpl.rc('font', family='Times New Roman')

# Use muted colors for bars
plt.barh(x - bar_width / 2, mean_ranking, bar_width, label="Mean Ranking", color="#4c91d9")  # Muted teal
plt.barh(x + bar_width / 2, most_common_ranking, bar_width, label="Most Common Ranking", color="#9a6fb0")  # Deep purple

# Customizing the chart
plt.yticks(x, x_order, fontsize=18)  # Larger font size for y-axis labels
plt.xlabel("Ranking", fontsize=18)  # Larger font size for x-axis label
plt.xticks(fontsize=14)  # Larger font size for x-axis tick values
plt.title("Mean and Most Common Rankings for Not Accepting Medicare", fontsize=18)  # Larger title
plt.gca().invert_yaxis()  # Invert y-axis to make 1 appear "largest"
plt.legend(fontsize=14)  # Larger legend font size
plt.tight_layout()

# Save the chart as an image
plt.savefig("cr_medicare_rankings_chart.png")

# Show the chart
plt.show()



# %%
###
# %%
#### [TABLES FOR ALL OF THE OTHER RANKINGS]
####

##demographic licensure check: 
# %%
# Subset the DataFrame
df1_license = df1[
    (df1["exclusionstatus"] == "include") & 
    (df1["hdt_complete"] == "Complete")
][["record_id", "What is your license type?"]]
# %%
##
##
from docx import Document

# Create a table summarizing license types and their counts
license_counts = df1_license["What is your license type?"].value_counts().reset_index()
license_counts.columns = ["License Type", "Number"]

# Save the table to a Word document
doc = Document()
doc.add_heading("HDT License Demographics", level=2)

# Add the table to the Word document
table = doc.add_table(license_counts.shape[0] + 1, license_counts.shape[1])
table.style = "Table Grid"

# Add column headers
for col_num, col_name in enumerate(license_counts.columns):
    table.cell(0, col_num).text = col_name

# Add the data rows
for row_num, row in license_counts.iterrows():
    for col_num, value in enumerate(row):
        table.cell(row_num + 1, col_num).text = str(value)

# Save the Word document
try:
    doc.save("/Users/dannyzweben/Desktop/CAADC/acs_datacleaning/HDT_License_Demographics.docx")
    print("Word document 'HDT_License_Demographics.docx' has been created and saved successfully!")
except Exception as e:
    print(f"Error saving HDT_License_Demographics.docx: {e}")

# %%
from docx import Document
import pandas as pd

# Assuming df_cr_data is your DataFrame

# Calculate mean, median, and mode for each reason
stats = df_cr_data[
    [
        "Reimbursement rates are too low.1", 
        "Administrative burden of submitting claims.1", 
        "Delays in getting paid.1", 
        "Concerns about treatment regulations.1", 
        "Concerns about audit risk.1", 
        "Not accepted onto an insurance panel.1"
    ]
].agg(["mean", "median", lambda x: x.mode().iloc[0]])  # Get the mode's first value

# Rename the lambda function column
stats.rename(index={"<lambda_0>": "mode"}, inplace=True)

# Transpose the table for readability
cr_medicaid_stats_table = stats.T.reset_index()
cr_medicaid_stats_table.columns = ["Reason", "Mean Ranking", "Median Ranking", "Most Common Ranking"]

cr_medicaid_stats_table["Mean Ranking"] = cr_medicaid_stats_table["Mean Ranking"].round(2)

# Save the table to a Word document
doc = Document()
doc.add_heading("Rankings of Reasons for Not Accepting Medicaid", level=2)

# Add the table to the Word document
table = doc.add_table(cr_medicaid_stats_table.shape[0] + 1, cr_medicaid_stats_table.shape[1])
table.style = "Table Grid"

# Add column headers
for col_num, col_name in enumerate(cr_medicaid_stats_table.columns):
    table.cell(0, col_num).text = col_name

# Add the data rows
for row_num, row in cr_medicaid_stats_table.iterrows():
    for col_num, value in enumerate(row):
        table.cell(row_num + 1, col_num).text = str(value)

# Save the Word document
try:
    doc.save("/Users/dannyzweben/Desktop/CAADC/acs_datacleaning/cr_medicaid_stats_table.docx")
    print("Word document 'cr_medicaid_stats_table.docx' has been created and saved successfully!")
except Exception as e:
    print(f"Error saving cr_medicaid_stats_table.docx: {e}")

# %%
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

# Custom order for the x-axis with added line breaks for long labels
x_order = [
    "Reimbursement rates\nare too low",
    "Administrative burden\nof submitting claims",
    "Delays in\ngetting paid",
    "Concerns about\ntreatment regulations",
    "Concerns about\naudit risk",
    "Not accepted onto\nan insurance panel"
]

# Ensure cr_medicaid_stats_table is sorted in this order
cr_medicaid_stats_table = cr_medicaid_stats_table.set_index("Reason").reindex(
    [
        "Reimbursement rates are too low.1",
        "Administrative burden of submitting claims.1",
        "Delays in getting paid.1",
        "Concerns about treatment regulations.1",
        "Concerns about audit risk.1",
        "Not accepted onto an insurance panel.1"
    ]
).reset_index()

# Data for the chart
x = np.arange(len(x_order))  # X-axis positions
mean_ranking = cr_medicaid_stats_table["Mean Ranking"]
most_common_ranking = cr_medicaid_stats_table["Most Common Ranking"]

# Plot grouped horizontal bars
plt.figure(figsize=(12, 8))  # Increased figure size for better readability
bar_width = 0.4

# Set the font to Times New Roman
mpl.rc('font', family='Times New Roman')

# Use muted colors for bars
plt.barh(x - bar_width / 2, mean_ranking, bar_width, label="Mean Ranking", color="#4c91d9")  # Muted teal
plt.barh(x + bar_width / 2, most_common_ranking, bar_width, label="Most Common Ranking", color="#9a6fb0")  # Deep purple

# Customizing the chart
plt.yticks(x, x_order, fontsize=18)  # Larger font size for y-axis labels
plt.xlabel("Ranking", fontsize=18)  # Larger font size for x-axis label
plt.xticks(fontsize=14)  # Larger font size for x-axis tick values
plt.title("Mean and Most Common Rankings for Not Accepting Medicaid", fontsize=18)  # Larger title
plt.gca().invert_yaxis()  # Invert y-axis to make 1 appear "largest"
plt.legend(fontsize=14)  # Larger legend font size
plt.tight_layout()

# Save the chart as an image
plt.savefig("cr_medicaid_rankings_chart.png")

# Show the chart
plt.show()

#%%
from docx import Document
import pandas as pd

# Assuming df_cr_data is your DataFrame

# Calculate mean, median, and mode for each reason
stats = df_cr_data[
    [
        "Reimbursement rates are too low.2", 
        "Administrative burden of submitting claims.2", 
        "Delays in getting paid.2", 
        "Concerns about treatment regulations.2", 
        "Concerns about audit risk.2", 
        "Not accepted onto an insurance panel.2"
    ]
].agg(["mean", "median", lambda x: x.mode().iloc[0]])  # Get the mode's first value

# Rename the lambda function column
stats.rename(index={"<lambda_0>": "mode"}, inplace=True)

# Transpose the table for readability
cr_privatepay_stats_table = stats.T.reset_index()
cr_privatepay_stats_table.columns = ["Reason", "Mean Ranking", "Median Ranking", "Most Common Ranking"]

cr_privatepay_stats_table["Mean Ranking"] = cr_privatepay_stats_table["Mean Ranking"].round(2)

# Save the table to a Word document
doc = Document()
doc.add_heading("Rankings of Reasons for Not Accepting Private Pay", level=2)

# Add the table to the Word document
table = doc.add_table(cr_privatepay_stats_table.shape[0] + 1, cr_privatepay_stats_table.shape[1])
table.style = "Table Grid"

# Add column headers
for col_num, col_name in enumerate(cr_privatepay_stats_table.columns):
    table.cell(0, col_num).text = col_name

# Add the data rows
for row_num, row in cr_privatepay_stats_table.iterrows():
    for col_num, value in enumerate(row):
        table.cell(row_num + 1, col_num).text = str(value)

# Save the Word document
try:
    doc.save("/Users/dannyzweben/Desktop/CAADC/acs_datacleaning/cr_privatepay_stats_table.docx")
    print("Word document 'cr_privatepay_stats_table.docx' has been created and saved successfully!")
except Exception as e:
    print(f"Error saving cr_privatepay_stats_table.docx: {e}")

# %%
# Filter the DataFrame for rows where `cr_complete` is "Complete" and select specific columns
df_demo_cr = df1.loc[
    (df1["cr_complete"] == "Complete") & (df1["exclusionstatus"] == "include"),
    [
        "record_id",
        "What is your fee for clients who pay using self pay?",
        "Do you offer a sliding scale?",
        "What is the lowest fee you offer clients?",
        "What is your estimated annual income?",
        "What is your license type?",
        "Please provide your NPI number (this will only be used to verify your identity to protect against fake participants; the confidentiality of your answers will be maintained):",
        "In what context do you practice the majority of your therapy?  ",
        "In which area do you primarily provide therapy you provide services in primarily:  ",
        "How do you identify racially/ethnically?  ",
        "How do you describe your current gender identity?",
        "Do you identify as transgender?"
    ]
]

# %%
#Table 1 - demographic information: 
from docx import Document

# Convert relevant columns to numeric
df_demo_cr["What is your fee for clients who pay using self pay?"] = pd.to_numeric(
    df_demo_cr["What is your fee for clients who pay using self pay?"], errors="coerce"
)
df_demo_cr["What is the lowest fee you offer clients?"] = pd.to_numeric(
    df_demo_cr["What is the lowest fee you offer clients?"], errors="coerce"
)
df_demo_cr["What is your estimated annual income?"] = pd.to_numeric(
    df_demo_cr["What is your estimated annual income?"], errors="coerce"
)

# Calculate statistics for numeric variables
self_pay_fee_mean = df_demo_cr["What is your fee for clients who pay using self pay?"].mean(skipna=True)
self_pay_fee_median = df_demo_cr["What is your fee for clients who pay using self pay?"].median(skipna=True)
self_pay_fee_n = df_demo_cr["What is your fee for clients who pay using self pay?"].count()

lowest_sliding_fee_mean = df_demo_cr["What is the lowest fee you offer clients?"].mean(skipna=True)
lowest_sliding_fee_median = df_demo_cr["What is the lowest fee you offer clients?"].median(skipna=True)

estimated_income_mean = df_demo_cr["What is your estimated annual income?"].mean(skipna=True)
estimated_income_median = df_demo_cr["What is your estimated annual income?"].median(skipna=True)
estimated_income_n = df_demo_cr["What is your estimated annual income?"].count()

# Calculate counts and percentages for categorical variables
sliding_scale_counts = df_demo_cr["Do you offer a sliding scale?"].value_counts()
license_type_counts = df_demo_cr["What is your license type?"].value_counts()
practice_context_counts = df_demo_cr["In what context do you practice the majority of your therapy?  "].value_counts()
service_area_counts = df_demo_cr["In which area do you primarily provide therapy you provide services in primarily:  "].value_counts()

# Calculate total rows dynamically
total_rows = (
    6  # Base rows (Payment Information + Estimated Annual Income)
    + len(license_type_counts) + 1  # License Type rows + Header
    + len(practice_context_counts) + 1  # Practice Context rows + Header
    + len(service_area_counts) + 1  # Service Area rows + Header
)

# Create a Word document
doc = Document()

# Add a title to the document
doc.add_heading('Demographic Data Summary', level=1)

# Add a heading for Table 1
doc.add_heading('Table 1: Payment Information', level=2)

# Create a table in the Word document with calculated rows
table = doc.add_table(rows=total_rows, cols=5)
table.style = 'Table Grid'

# Add column headers
headers = ["Variable", "Mean", "Median", "n", "%"]
for i, header in enumerate(headers):
    table.cell(0, i).text = header

# Populate Payment Information rows
data = [
    ["Self-Pay Fee", f"${self_pay_fee_mean:.2f}", f"${self_pay_fee_median:.2f}", self_pay_fee_n, "-"],
    ["Sliding Scale Offered (Yes)", "-", "-", sliding_scale_counts.get("Yes", 0), f"{(sliding_scale_counts.get('Yes', 0) / sliding_scale_counts.sum()) * 100:.1f}%"],
    ["Sliding Scale Offered (No)", "-", "-", sliding_scale_counts.get("No", 0), f"{(sliding_scale_counts.get('No', 0) / sliding_scale_counts.sum()) * 100:.1f}%"],
    ["Lowest Sliding Scale Fee", f"${lowest_sliding_fee_mean:.2f}", f"${lowest_sliding_fee_median:.2f}", "-", "-"],
    ["Estimated Annual Income", f"${estimated_income_mean:.2f}", f"${estimated_income_median:.2f}", estimated_income_n, "-"],
    ["License Type", "-", "-", "-", "-"]  # Header row for License Type
]

row_idx = 1
for row_data in data:
    for col_idx, value in enumerate(row_data):
        table.cell(row_idx, col_idx).text = str(value)
    row_idx += 1

# Add rows for License Type
for license_type, count in license_type_counts.items():
    percent = (count / license_type_counts.sum()) * 100
    row = [license_type, "-", "-", count, f"{percent:.1f}%"]
    for col_idx, value in enumerate(row):
        table.cell(row_idx, col_idx).text = str(value)
    row_idx += 1

# Add header row for Practice Context
table.cell(row_idx, 0).text = "Practice Context"
for col_idx in range(1, 5):
    table.cell(row_idx, col_idx).text = "-"
row_idx += 1

# Add rows for Practice Context
for context, count in practice_context_counts.items():
    percent = (count / practice_context_counts.sum()) * 100
    row = [context, "-", "-", count, f"{percent:.1f}%"]
    for col_idx, value in enumerate(row):
        table.cell(row_idx, col_idx).text = str(value)
    row_idx += 1

# Add header row for Service Area
table.cell(row_idx, 0).text = "Service Area"
for col_idx in range(1, 5):
    table.cell(row_idx, col_idx).text = "-"
row_idx += 1

# Add rows for Service Area
for area, count in service_area_counts.items():
    percent = (count / service_area_counts.sum()) * 100
    row = [area, "-", "-", count, f"{percent:.1f}%"]
    for col_idx, value in enumerate(row):
        table.cell(row_idx, col_idx).text = str(value)
    row_idx += 1

# Save the Word document
try:
    doc.save("/Users/dannyzweben/Desktop/CAADC/acs_datacleaning/demo_alldata.docx")
    print("Table 1 with additional rows has been added to 'demo_alldata.docx' and saved successfully!")
except Exception as e:
    print(f"Error saving demo_alldata.docx: {e}")

# %%
##SD CALCULATIONS: 

# Convert relevant columns to numeric
df_demo_cr["What is your fee for clients who pay using self pay?"] = pd.to_numeric(
    df_demo_cr["What is your fee for clients who pay using self pay?"], errors="coerce"
)
df_demo_cr["What is the lowest fee you offer clients?"] = pd.to_numeric(
    df_demo_cr["What is the lowest fee you offer clients?"], errors="coerce"
)
df_demo_cr["What is your estimated annual income?"] = pd.to_numeric(
    df_demo_cr["What is your estimated annual income?"], errors="coerce"
)

# Calculate standard deviations
self_pay_fee_sd = df_demo_cr["What is your fee for clients who pay using self pay?"].std(skipna=True)
lowest_sliding_fee_sd = df_demo_cr["What is the lowest fee you offer clients?"].std(skipna=True)
estimated_income_sd = df_demo_cr["What is your estimated annual income?"].std(skipna=True)

# Print the results
print(f"Standard Deviation for Self-Pay Fee: ${self_pay_fee_sd:.2f}")
print(f"Standard Deviation for Lowest Sliding Scale Fee: ${lowest_sliding_fee_sd:.2f}")
print(f"Standard Deviation for Estimated Annual Income: ${estimated_income_sd:.2f}")

# %%



df_demo_hdt = df1.loc[
    (df1["hdt_complete"] == "Complete") & (df1["exclusionstatus"] == "include"),
    [
        "record_id",
        "What is your fee for clients who pay using self pay?",
        "Do you offer a sliding scale?",
        "What is the lowest fee you offer clients?",
        "What is your estimated annual income?",
        "What is your license type?",
        "Please provide your NPI number (this will only be used to verify your identity to protect against fake participants; the confidentiality of your answers will be maintained):",
        "In what context do you practice the majority of your therapy?  ",
        "In which area do you primarily provide therapy you provide services in primarily:  ",
        "How do you identify racially/ethnically?  ",
        "How do you describe your current gender identity?",
        "Do you identify as transgender?"
    ]
]

#%%
lowest_sliding_fee_n = df_demo_cr["What is the lowest fee you offer clients?"].count()

# Print the result
print(f"N for Lowest Sliding Scale Fee: {lowest_sliding_fee_n}")



# %%
### HDT CALCULATIONS: 

#Table 1 - demographic information: 
from docx import Document

# Convert relevant columns to numeric
df_demo_hdt["What is your fee for clients who pay using self pay?"] = pd.to_numeric(
    df_demo_hdt["What is your fee for clients who pay using self pay?"], errors="coerce"
)
df_demo_hdt["What is the lowest fee you offer clients?"] = pd.to_numeric(
    df_demo_hdt["What is the lowest fee you offer clients?"], errors="coerce"
)
df_demo_hdt["What is your estimated annual income?"] = pd.to_numeric(
    df_demo_hdt["What is your estimated annual income?"], errors="coerce"
)

# Calculate statistics for numeric variables
self_pay_fee_mean = df_demo_hdt["What is your fee for clients who pay using self pay?"].mean(skipna=True)
self_pay_fee_median = df_demo_hdt["What is your fee for clients who pay using self pay?"].median(skipna=True)
self_pay_fee_n = df_demo_hdt["What is your fee for clients who pay using self pay?"].count()

lowest_sliding_fee_mean = df_demo_hdt["What is the lowest fee you offer clients?"].mean(skipna=True)
lowest_sliding_fee_median = df_demo_hdt["What is the lowest fee you offer clients?"].median(skipna=True)

estimated_income_mean = df_demo_hdt["What is your estimated annual income?"].mean(skipna=True)
estimated_income_median = df_demo_hdt["What is your estimated annual income?"].median(skipna=True)
estimated_income_n = df_demo_hdt["What is your estimated annual income?"].count()

# Calculate counts and percentages for categorical variables
sliding_scale_counts = df_demo_hdt["Do you offer a sliding scale?"].value_counts()
license_type_counts = df_demo_hdt["What is your license type?"].value_counts()
practice_context_counts = df_demo_hdt["In what context do you practice the majority of your therapy?  "].value_counts()
service_area_counts = df_demo_hdt["In which area do you primarily provide therapy you provide services in primarily:  "].value_counts()

# Calculate total rows dynamically
total_rows = (
    6  # Base rows (Payment Information + Estimated Annual Income)
    + len(license_type_counts) + 1  # License Type rows + Header
    + len(practice_context_counts) + 1  # Practice Context rows + Header
    + len(service_area_counts) + 1  # Service Area rows + Header
)

# Create a Word document
doc = Document()

# Add a title to the document
doc.add_heading('Demographic Data Summary', level=1)

# Add a heading for Table 1
doc.add_heading('Table 1: Payment Information', level=2)

# Create a table in the Word document with calculated rows
table = doc.add_table(rows=total_rows, cols=5)
table.style = 'Table Grid'

# Add column headers
headers = ["Variable", "Mean", "Median", "n", "%"]
for i, header in enumerate(headers):
    table.cell(0, i).text = header

# Populate Payment Information rows
data = [
    ["Self-Pay Fee", f"${self_pay_fee_mean:.2f}", f"${self_pay_fee_median:.2f}", self_pay_fee_n, "-"],
    ["Sliding Scale Offered (Yes)", "-", "-", sliding_scale_counts.get("Yes", 0), f"{(sliding_scale_counts.get('Yes', 0) / sliding_scale_counts.sum()) * 100:.1f}%"],
    ["Sliding Scale Offered (No)", "-", "-", sliding_scale_counts.get("No", 0), f"{(sliding_scale_counts.get('No', 0) / sliding_scale_counts.sum()) * 100:.1f}%"],
    ["Lowest Sliding Scale Fee", f"${lowest_sliding_fee_mean:.2f}", f"${lowest_sliding_fee_median:.2f}", "-", "-"],
    ["Estimated Annual Income", f"${estimated_income_mean:.2f}", f"${estimated_income_median:.2f}", estimated_income_n, "-"],
    ["License Type", "-", "-", "-", "-"]  # Header row for License Type
]

row_idx = 1
for row_data in data:
    for col_idx, value in enumerate(row_data):
        table.cell(row_idx, col_idx).text = str(value)
    row_idx += 1

# Add rows for License Type
for license_type, count in license_type_counts.items():
    percent = (count / license_type_counts.sum()) * 100
    row = [license_type, "-", "-", count, f"{percent:.1f}%"]
    for col_idx, value in enumerate(row):
        table.cell(row_idx, col_idx).text = str(value)
    row_idx += 1

# Add header row for Practice Context
table.cell(row_idx, 0).text = "Practice Context"
for col_idx in range(1, 5):
    table.cell(row_idx, col_idx).text = "-"
row_idx += 1

# Add rows for Practice Context
for context, count in practice_context_counts.items():
    percent = (count / practice_context_counts.sum()) * 100
    row = [context, "-", "-", count, f"{percent:.1f}%"]
    for col_idx, value in enumerate(row):
        table.cell(row_idx, col_idx).text = str(value)
    row_idx += 1

# Add header row for Service Area
table.cell(row_idx, 0).text = "Service Area"
for col_idx in range(1, 5):
    table.cell(row_idx, col_idx).text = "-"
row_idx += 1

# Add rows for Service Area
for area, count in service_area_counts.items():
    percent = (count / service_area_counts.sum()) * 100
    row = [area, "-", "-", count, f"{percent:.1f}%"]
    for col_idx, value in enumerate(row):
        table.cell(row_idx, col_idx).text = str(value)
    row_idx += 1

# Save the Word document
try:
    doc.save("/Users/dannyzweben/Desktop/CAADC/acs_datacleaning/demo_hdtdata.docx")
    print("Table 1 with additional rows has been added to 'demo_hdtdata.docx' and saved successfully!")
except Exception as e:
    print(f"Error saving demo_hdtdata.docx: {e}")
# %%
from docx import Document

# Calculate counts and percentages for each variable
race_ethnicity_counts = df_demo_cr["How do you identify racially/ethnically?  "].value_counts()
gender_identity_counts = df_demo_cr["How do you describe your current gender identity?"].value_counts()
transgender_counts = df_demo_cr["Do you identify as transgender?"].value_counts()

race_ethnicity_total = race_ethnicity_counts.sum()
gender_identity_total = gender_identity_counts.sum()
transgender_total = transgender_counts.sum()

# Create a new Word document
doc = Document()

# Add a title
doc.add_heading("Participant Demographics", level=1)

# Add a heading for the table
doc.add_heading("Table 2: Participant Demographics", level=2)

# Create the table
total_rows = (
    1  # Header row
    + len(race_ethnicity_counts)  # Rows for Race/Ethnicity
    + len(gender_identity_counts)  # Rows for Gender Identity
    + len(transgender_counts)  # Rows for Transgender Identification
    + 3  # Header rows for each variable
)
table = doc.add_table(rows=total_rows, cols=4)
table.style = "Table Grid"

# Add column headers
headers = ["Variable", "Category", "n", "%"]
for col_idx, header in enumerate(headers):
    table.cell(0, col_idx).text = header

# Add data for Race/Ethnicity
row_idx = 1
table.cell(row_idx, 0).text = "Race/Ethnicity"
for col_idx in range(1, 4):
    table.cell(row_idx, col_idx).text = "-"
row_idx += 1

for category, count in race_ethnicity_counts.items():
    percent = (count / race_ethnicity_total) * 100
    row = ["", category, count, f"{percent:.1f}%"]
    for col_idx, value in enumerate(row):
        table.cell(row_idx, col_idx).text = str(value)
    row_idx += 1

# Add data for Gender Identity
table.cell(row_idx, 0).text = "Gender Identity"
for col_idx in range(1, 4):
    table.cell(row_idx, col_idx).text = "-"
row_idx += 1

for category, count in gender_identity_counts.items():
    percent = (count / gender_identity_total) * 100
    row = ["", category, count, f"{percent:.1f}%"]
    for col_idx, value in enumerate(row):
        table.cell(row_idx, col_idx).text = str(value)
    row_idx += 1

# Add data for Transgender Identification
table.cell(row_idx, 0).text = "Transgender Identification"
for col_idx in range(1, 4):
    table.cell(row_idx, col_idx).text = "-"
row_idx += 1

for category, count in transgender_counts.items():
    percent = (count / transgender_total) * 100
    row = ["", category, count, f"{percent:.1f}%"]
    for col_idx, value in enumerate(row):
        table.cell(row_idx, col_idx).text = str(value)
    row_idx += 1

# Save the document
try:
    doc.save("/Users/dannyzweben/Desktop/CAADC/acs_datacleaning/participant_demographics.docx")
    print("Table 2: Participant Demographics has been added to 'participant_demographics.docx' and saved successfully!")
except Exception as e:
    print(f"Error saving participant_demographics.docx: {e}")

# %%
from docx import Document

# Calculate counts and percentages for each variable
race_ethnicity_counts = df_demo_hdt["How do you identify racially/ethnically?  "].value_counts()
gender_identity_counts = df_demo_hdt["How do you describe your current gender identity?"].value_counts()
transgender_counts = df_demo_hdt["Do you identify as transgender?"].value_counts()

race_ethnicity_total = race_ethnicity_counts.sum()
gender_identity_total = gender_identity_counts.sum()
transgender_total = transgender_counts.sum()

# Create a new Word document
doc = Document()

# Add a title
doc.add_heading("Participant Demographics", level=1)

# Add a heading for the table
doc.add_heading("Table 2: Participant Demographics", level=2)

# Create the table
total_rows = (
    1  # Header row
    + len(race_ethnicity_counts)  # Rows for Race/Ethnicity
    + len(gender_identity_counts)  # Rows for Gender Identity
    + len(transgender_counts)  # Rows for Transgender Identification
    + 3  # Header rows for each variable
)
table = doc.add_table(rows=total_rows, cols=4)
table.style = "Table Grid"

# Add column headers
headers = ["Variable", "Category", "n", "%"]
for col_idx, header in enumerate(headers):
    table.cell(0, col_idx).text = header

# Add data for Race/Ethnicity
row_idx = 1
table.cell(row_idx, 0).text = "Race/Ethnicity"
for col_idx in range(1, 4):
    table.cell(row_idx, col_idx).text = "-"
row_idx += 1

for category, count in race_ethnicity_counts.items():
    percent = (count / race_ethnicity_total) * 100
    row = ["", category, count, f"{percent:.1f}%"]
    for col_idx, value in enumerate(row):
        table.cell(row_idx, col_idx).text = str(value)
    row_idx += 1

# Add data for Gender Identity
table.cell(row_idx, 0).text = "Gender Identity"
for col_idx in range(1, 4):
    table.cell(row_idx, col_idx).text = "-"
row_idx += 1

for category, count in gender_identity_counts.items():
    percent = (count / gender_identity_total) * 100
    row = ["", category, count, f"{percent:.1f}%"]
    for col_idx, value in enumerate(row):
        table.cell(row_idx, col_idx).text = str(value)
    row_idx += 1

# Add data for Transgender Identification
table.cell(row_idx, 0).text = "Transgender Identification"
for col_idx in range(1, 4):
    table.cell(row_idx, col_idx).text = "-"
row_idx += 1

for category, count in transgender_counts.items():
    percent = (count / transgender_total) * 100
    row = ["", category, count, f"{percent:.1f}%"]
    for col_idx, value in enumerate(row):
        table.cell(row_idx, col_idx).text = str(value)
    row_idx += 1

# Save the document
try:
    doc.save("/Users/dannyzweben/Desktop/CAADC/acs_datacleaning/hdt_participant_demographics.docx")
    print("Table 2: Participant Demographics has been added to 'hdt_participant_demographics.docx' and saved successfully!")
except Exception as e:
    print(f"Error saving hdt_participant_demographics.docx: {e}")

# %%
##### Double Checking criteria ranking medicare numbers: 
### rerun checks at the end after manually applying braching logic. 

## MEDICARE: 54', '47', '57', '43', '60' all didn't meet criteria to be given that survey but were given it anyway...
## MEDICADE: 9', '140', '43', '186'
###Remove these above ^^

#%%
### re ran below with medicare and private pay exclusion critaria
import pandas as pd

# Ensure 'record_id' is the same type in all dataframes
df1["record_id"] = df1["record_id"].astype(str)
df1_cr["record_id"] = df1_cr["record_id"].astype(str)
medicare_check_df["record_id"] = medicare_check_df["record_id"].astype(str)

# Merge df1_cr and medicare_check_df first, keeping exclusionstatus from df1_cr
merged_df = df1_cr.merge(medicare_check_df, on="record_id", how="inner", suffixes=("", "_drop"))

# Drop the duplicate 'exclusionstatus' column if it exists
merged_df = merged_df.drop(columns=[col for col in merged_df.columns if "exclusionstatus_drop" in col], errors="ignore")

# Merge with df1 while keeping columns from previous merge
merged_df = merged_df.merge(df1, on="record_id", how="inner", suffixes=("", "_df1"))

# Print column names to verify existence of necessary columns
print("Merged DataFrame Columns:", merged_df.columns.tolist())

# Get record IDs for the first criteria (From df1_cr and df1)
criteria_1_ids = set(merged_df[
    (merged_df["criteria ranking"] == "Complete") & 
    (merged_df["exclusionstatus"] == "include") & 
    merged_df["Administrative burden of submitting claims"].notna() & 
    (merged_df["Administrative burden of submitting claims"] != "")
]["record_id"])

# Get record IDs for the second criteria (From df1_cr and medicare_check_df)
criteria_2_ids = set(merged_df[
    (merged_df["criteria ranking"] == "Complete") & 
    (merged_df["exclusionstatus"] == "include") & 
    (merged_df["accepted_insurance_plans___3"] == '0') & 
    (merged_df["medicare_population"] == '1')
]["record_id"])

# Find record IDs that are in one set but not the other
difference_ids = criteria_1_ids.symmetric_difference(criteria_2_ids)

# Print the record IDs
print("Record IDs meeting one criteria but not the other:", difference_ids)

# %%
import pandas as pd

# Ensure 'record_id' is the same type in all dataframes
df1["record_id"] = df1["record_id"].astype(str)
df1_cr["record_id"] = df1_cr["record_id"].astype(str)
medicare_check_df["record_id"] = medicare_check_df["record_id"].astype(str)

# Merge df1_cr and medicare_check_df first, keeping exclusionstatus from df1_cr
merged_df = df1_cr.merge(medicare_check_df, on="record_id", how="inner", suffixes=("", "_drop"))

# Drop the duplicate 'exclusionstatus' column if it exists
merged_df = merged_df.drop(columns=[col for col in merged_df.columns if "exclusionstatus_drop" in col], errors="ignore")

# Merge with df1 while keeping columns from previous merge
merged_df = merged_df.merge(df1, on="record_id", how="inner", suffixes=("", "_df1"))

# Print column names to verify existence of necessary columns
print("Merged DataFrame Columns:", merged_df.columns.tolist())

# Get record IDs for the first criteria (From df1_cr and df1)
criteria_1_ids = set(merged_df[
    (merged_df["criteria ranking"] == "Complete") & 
    (merged_df["exclusionstatus"] == "include") & 
    merged_df["Administrative burden of submitting claims.1"].notna() & 
    (merged_df["Administrative burden of submitting claims.1"] != "")
]["record_id"])

# Get record IDs for the second criteria (From df1_cr and medicare_check_df)
criteria_2_ids = set(merged_df[
    (merged_df["criteria ranking"] == "Complete") & 
    (merged_df["exclusionstatus"] == "include") & 
    (merged_df["accepted_insurance_plans___2"] == '0')
]["record_id"])

# Find record IDs that are in one set but not the other
difference_ids = criteria_1_ids.symmetric_difference(criteria_2_ids)

# Print counts and differences
print(f"Total meeting first criteria: {len(criteria_1_ids)}")
print(f"Total meeting second criteria: {len(criteria_2_ids)}")
print(f"Record IDs meeting one criteria but not the other ({len(difference_ids)} total): {difference_ids}")

#%%
### inegligablity data pull

# ...existing code...
import pandas as pd
from redcap import Project

# Initialize REDCap project
api_url = "https://cphapps.temple.edu/redcap/api/"
api_token = "REMOVED"
project = Project(api_url, api_token)

# Pull the data from REDCap
fields = [
    'record_id', 'licensed_provider', 'private_practice', 
    'client_hours', 'insurance_decision', 
    'in_network_reimbursement_v2', 'individual_therapy_v2',
    'screening_complete', 'how_did_you_find_out_about'
]
data = project.export_records(fields=fields)

# Convert the data to a DataFrame
df_ineligable = pd.DataFrame(data)

# Print the count of how many people had a 0 or '0' for the column licensed_provider
licensed_provider_count = df_ineligable[(df_ineligable['licensed_provider'] == 0) | (df_ineligable['licensed_provider'] == '0')].shape[0]
print(f"Count of licensed_provider == 0: {licensed_provider_count}")

# Print the count for the specified conditions
private_practice_count = df_ineligable[df_ineligable['private_practice'] == 0].shape[0] + df_ineligable[df_ineligable['private_practice'] == '0'].shape[0]
client_hours_count = df_ineligable[df_ineligable['client_hours'] == 2].shape[0] + df_ineligable[df_ineligable['client_hours'] == '2'].shape[0]
insurance_decision_count = df_ineligable[df_ineligable['insurance_decision'] == 0].shape[0] + df_ineligable[df_ineligable['insurance_decision'] == '0'].shape[0]
in_network_reimbursement_v2_count = df_ineligable[df_ineligable['in_network_reimbursement_v2'] == 2].shape[0] + df_ineligable[df_ineligable['in_network_reimbursement_v2'] == '2'].shape[0]
individual_therapy_v2_count = df_ineligable[df_ineligable['individual_therapy_v2'] == 1].shape[0] + df_ineligable[df_ineligable['individual_therapy_v2'] == '1'].shape[0]


print(f"Count of private_practice == 0: {private_practice_count}")
print(f"Count of client_hours == 2: {client_hours_count}")
print(f"Count of insurance_decision == 0: {insurance_decision_count}")
print(f"Count of in_network_reimbursement_v2 == 2: {in_network_reimbursement_v2_count}")
print(f"Count of individual_therapy_v2 == 1: {individual_therapy_v2_count}")


##### DEBUGGING TIME!
# Get the record IDs for each condition
licensed_provider_ids = df_ineligable[(df_ineligable['licensed_provider'] == 0) | (df_ineligable['licensed_provider'] == '0')]['record_id']
private_practice_ids = df_ineligable[(df_ineligable['private_practice'] == 0) | (df_ineligable['private_practice'] == '0')]['record_id']
client_hours_ids = df_ineligable[(df_ineligable['client_hours'] == 2) | (df_ineligable['client_hours'] == '2')]['record_id']
insurance_decision_ids = df_ineligable[(df_ineligable['insurance_decision'] == 0) | (df_ineligable['insurance_decision'] == '0')]['record_id']
in_network_reimbursement_v2_ids = df_ineligable[(df_ineligable['in_network_reimbursement_v2'] == 2) | (df_ineligable['in_network_reimbursement_v2'] == '2')]['record_id']
individual_therapy_v2_ids = df_ineligable[(df_ineligable['individual_therapy_v2'] == 1) | (df_ineligable['individual_therapy_v2'] == '1')]['record_id']

# Combine all the record IDs into a single series
all_record_ids_series = pd.concat([
    licensed_provider_ids, private_practice_ids, client_hours_ids,
    insurance_decision_ids, in_network_reimbursement_v2_ids, individual_therapy_v2_ids
])

# Count the occurrences of each record ID
record_id_counts = all_record_ids_series.value_counts()

# Identify record IDs that met more than one criterion
multiple_criteria_ids = record_id_counts[record_id_counts > 1]

# Print the record IDs that met more than one criterion and their counts
if not multiple_criteria_ids.empty:
    print("Record IDs that met more than one criterion:")
    print(multiple_criteria_ids)
else:
    print("No record IDs met more than one criterion.")
# %%
#### calculate just incomplete: 

# Count the number of people who met the criteria but didn't meet any of the specified conditions
criteria_not_met_count = df1_cr[
    (df1_cr["criteria ranking"] != "Complete") & 
    (df1_cr["exclusionstatus"] == "include") & 
    ~((df_ineligable['licensed_provider'] == 0) | (df_ineligable['licensed_provider'] == '0') |
      (df_ineligable['private_practice'] == 0) | (df_ineligable['private_practice'] == '0') |
      (df_ineligable['client_hours'] == 2) | (df_ineligable['client_hours'] == '2') |
      (df_ineligable['insurance_decision'] == 0) | (df_ineligable['insurance_decision'] == '0') |
      (df_ineligable['in_network_reimbursement_v2'] == 2) | (df_ineligable['in_network_reimbursement_v2'] == '2') |
      (df_ineligable['individual_therapy_v2'] == 1) | (df_ineligable['individual_therapy_v2'] == '1'))
].shape[0]

print(f"Count of people who met the criteria but didn't meet any of the specified conditions: {criteria_not_met_count}")


###### 115 incomplete (just stopped after screener for no reason)
#Count of licensed_provider == 0: 2
#Count of private_practice == 0: 12
#Count of client_hours == 2: 27
#Count of insurance_decision == 0: 7
#Count of in_network_reimbursement_v2 == 2: 169
#Count of individual_therapy_v2 == 1: 15


###Who to subtract?
## 87 and 563 wwere unliscend providers but the survey wasn't ended so they ended 
## also having other criteria that was disqualifying. (87 also worked in community 
# mental heatlh, and 563 also accepted > 50% in net work insurance). These were removed 
## from those second tallies because they should have already been removed from the survey, 
## and instead added to unliscened provider. 


### Getting updated scripts for CR completion rates excluding - 241, 409, 491


import pandas as pd

# Load the dataset
df = pd.read_csv("/Users/dannyzweben/Desktop/CAADC/acs_datacleaning/progress.csv")

# Exclude specific record IDs
excluded_ids = {241, 409, 491}
df = df[~df["record_id"].isin(excluded_ids)]

# Map degree group using explicit options from your form
df["degree_group"] = df["What is your license type?"].map({
    "PhD, PsyD": "Doc",
    "LCSW, LMSW, LICSW": "Non-Doc",
    "LPC": "Non-Doc",
    "LMFT": "Non-Doc",
    "LMHC": "Non-Doc"
})

# Keep only usable participants
df = df[df["exclusionstatus"] == "include"]

# Create completion flags for CR insurance sets
df["medicare_complete"] = df["Reimbursement rates are too low"].notna()
df["medicaid_complete"] = df["Reimbursement rates are too low.1"].notna()
df["private_complete"] = df["Reimbursement rates are too low.2"].notna()

# Group by degree group and sum completions
summary = df.groupby("degree_group")[["medicare_complete", "medicaid_complete", "private_complete"]].sum()

# Add total row
summary.loc["Total"] = summary.sum()

# Rename for clarity
summary.columns = ["Medicare", "Medicaid", "Private Insurance"]

# Display the summary
print("\nSummary of CR Completion by Degree Type (Excluding IDs 241, 409, 491):\n")
print(summary)

# %%
