# %%

import pandas as pd
import numpy as np

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

# Exclude the following record IDs from all analyses because they provided incorrect or incomplete sample data. 
excluded_ids = [241, 409, 491]
df1 = df1[~df1['record_id'].isin(excluded_ids)]


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
doc.save("Usable_Data.docx")
print("Word document 'Usable_Data.docx' has been created!")


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
doc = Document()

# Add a title for the table
doc.add_heading("Completion Summary", level=2)

# Add the table to the Word document
table = doc.add_table(ud_results_table.shape[0] + 1, ud_results_table.shape[1])
table.style = "Table Grid"

# Add column headers
for col_num, col_name in enumerate(ud_results_table.columns):
    table.cell(0, col_num).text = col_name

# Add the data rows
for row_num, row in ud_results_table.iterrows():
    for col_num, value in enumerate(row):
        table.cell(row_num + 1, col_num).text = str(value)

# Save the Word document
doc.save("Completion_Summary.docx")
#%%
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
df_cr_data = df1.loc[
    (df1['exclusionstatus'] == 'include'),
    existing_columns
]


# %%
### DECISIONS NOT TO ACCEPT MEDICARE: 
#Reimbursement rates are too low	Administrative burden of submitting claims	Delays in getting paid	Concerns about treatment regulations	Concerns about audit risk	Not accepted onto an insurance panel

# %%
# %%
from docx import Document
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

# Medicare stats: mean and standard deviation
stats = df_cr_data[
    [
        "Reimbursement rates are too low", 
        "Administrative burden of submitting claims", 
        "Delays in getting paid", 
        "Concerns about treatment regulations", 
        "Concerns about audit risk", 
        "Not accepted onto an insurance panel"
    ]
].agg(["mean", "std"])

cr_medicare_stats_table = stats.T.reset_index()
cr_medicare_stats_table.columns = ["Reason", "Mean Ranking", "Standard Deviation"]
cr_medicare_stats_table["Mean Ranking"] = cr_medicare_stats_table["Mean Ranking"].round(2)
cr_medicare_stats_table["Standard Deviation"] = cr_medicare_stats_table["Standard Deviation"].round(2)

doc = Document()
doc.add_heading("Mean and Standard Deviation: Reasons for Not Accepting Medicare", level=2)
table = doc.add_table(cr_medicare_stats_table.shape[0] + 1, cr_medicare_stats_table.shape[1])
table.style = "Table Grid"

for col_num, col_name in enumerate(cr_medicare_stats_table.columns):
    table.cell(0, col_num).text = col_name

for row_num, row in cr_medicare_stats_table.iterrows():
    for col_num, value in enumerate(row):
        table.cell(row_num + 1, col_num).text = str(value)

doc.save("/Users/dannyzweben/Desktop/CAADC/acs_datacleaning/ALL-cr_medicare_stats_table.docx")
print("Word document 'ALL-cr_medicare_stats_table.docx' has been created!")

# %%
# Medicaid stats
stats = df_cr_data[
    [
        "Reimbursement rates are too low.1", 
        "Administrative burden of submitting claims.1", 
        "Delays in getting paid.1", 
        "Concerns about treatment regulations.1", 
        "Concerns about audit risk.1", 
        "Not accepted onto an insurance panel.1"
    ]
].agg(["mean", "std"])

cr_medicaid_stats_table = stats.T.reset_index()
cr_medicaid_stats_table.columns = ["Reason", "Mean Ranking", "Standard Deviation"]
cr_medicaid_stats_table["Mean Ranking"] = cr_medicaid_stats_table["Mean Ranking"].round(2)
cr_medicaid_stats_table["Standard Deviation"] = cr_medicaid_stats_table["Standard Deviation"].round(2)

doc = Document()
doc.add_heading("Mean and Standard Deviation: Reasons for Not Accepting Medicaid", level=2)
table = doc.add_table(cr_medicaid_stats_table.shape[0] + 1, cr_medicaid_stats_table.shape[1])
table.style = "Table Grid"

for col_num, col_name in enumerate(cr_medicaid_stats_table.columns):
    table.cell(0, col_num).text = col_name

for row_num, row in cr_medicaid_stats_table.iterrows():
    for col_num, value in enumerate(row):
        table.cell(row_num + 1, col_num).text = str(value)

doc.save("/Users/dannyzweben/Desktop/CAADC/acs_datacleaning/ALL-cr_medicaid_stats_table.docx")
print("Word document 'ALL-cr_medicaid_stats_table.docx' has been created!")

# %%
from docx import Document
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

# Private Pay stats: Mean and SD
stats = df_cr_data[
    [
        "Reimbursement rates are too low.2", 
        "Administrative burden of submitting claims.2", 
        "Delays in getting paid.2", 
        "Concerns about treatment regulations.2", 
        "Concerns about audit risk.2", 
        "Not accepted onto an insurance panel.2"
    ]
].agg(["mean", "std"])

# Fix the table to only include clean mean and SD
cr_privatepay_stats_table = (
    stats.loc[["mean", "std"]]
    .T
    .reset_index()
    .rename(columns={"index": "Reason", "mean": "Mean Ranking", "std": "Standard Deviation"})
)

cr_privatepay_stats_table["Mean Ranking"] = cr_privatepay_stats_table["Mean Ranking"].round(2)
cr_privatepay_stats_table["Standard Deviation"] = cr_privatepay_stats_table["Standard Deviation"].round(2)

# Export to Word
doc = Document()
doc.add_heading("Mean and Standard Deviation: Reasons for Not Accepting Private Insurance", level=2)
table = doc.add_table(cr_privatepay_stats_table.shape[0] + 1, cr_privatepay_stats_table.shape[1])
table.style = "Table Grid"

for col_num, col_name in enumerate(cr_privatepay_stats_table.columns):
    table.cell(0, col_num).text = col_name

for row_num, row in cr_privatepay_stats_table.iterrows():
    for col_num, value in enumerate(row):
        table.cell(row_num + 1, col_num).text = str(value)

doc.save("/Users/dannyzweben/Desktop/CAADC/acs_datacleaning/ALL-cr_privatepay_stats_table.docx")
print("Word document 'ALL-cr_privatepay_stats_table.docx' has been created!")

# %%
# Chart (unchanged, just plotting Mean Ranking)
x_order = [
    "Reimbursement rates\nare too low",
    "Administrative burden\nof submitting claims",
    "Delays in\ngetting paid",
    "Concerns about\ntreatment regulations",
    "Concerns about\naudit risk",
    "Not accepted onto\nan insurance panel"
]

cr_privatepay_stats_table = cr_privatepay_stats_table.set_index("Reason").reindex(
    [
        "Reimbursement rates are too low.2",
        "Administrative burden of submitting claims.2",
        "Delays in getting paid.2",
        "Concerns about treatment regulations.2",
        "Concerns about audit risk.2",
        "Not accepted onto an insurance panel.2"
    ]
).reset_index()

x = np.arange(len(x_order))
mean_ranking = cr_privatepay_stats_table["Mean Ranking"]

plt.figure(figsize=(10, 6))
mpl.rc('font', family='Times New Roman')
plt.barh(x, mean_ranking, height=0.5, color="#4c91d9", label="Mean Ranking")
plt.yticks(x, x_order, fontsize=14)
plt.xlabel("Ranking", fontsize=14)
plt.xticks(fontsize=12)
plt.title("Mean Rankings for Not Accepting Private Insurance", fontsize=16)
plt.gca().invert_yaxis()
plt.legend(fontsize=12)
plt.tight_layout()
plt.savefig("cr_private_rankings_chart.png")
plt.show()


#%%


##### REMOVE Unbranched Clinicians:
# 
# import pandas as pd

# Define the record IDs and corresponding columns to modify
record_ids_set_1 = ['54', '47', '57', '43', '60']
columns_set_1 = [
    "Reimbursement rates are too low",
    "Administrative burden of submitting claims",
    "Delays in getting paid",
    "Concerns about treatment regulations",
    "Concerns about audit risk",
    "Not accepted onto an insurance panel"
]

record_ids_set_2 = ['9', '140', '43', '186']
columns_set_2 = [
    "Reimbursement rates are too low.1",
    "Administrative burden of submitting claims.1",
    "Delays in getting paid.1",
    "Concerns about treatment regulations.1",
    "Concerns about audit risk.1",
    "Not accepted onto an insurance panel.1"
]

# Convert record_id column to string to ensure consistency
df_cr_data['record_id'] = df_cr_data['record_id'].astype(str)

# Set the specified values to NA for the given record IDs
df_cr_data.loc[df_cr_data['record_id'].isin(record_ids_set_1), columns_set_1] = pd.NA
df_cr_data.loc[df_cr_data['record_id'].isin(record_ids_set_2), columns_set_2] = pd.NA 



# %%
# Count non-null values in the specified columns
count_1 = df_cr_data["Reimbursement rates are too low"].count()
count_2 = df_cr_data["Reimbursement rates are too low.1"].count()
count_3 = df_cr_data["Reimbursement rates are too low.2"].count()

# Print the counts
print(f"Count for 'Medicare-doc': {count_1}")
print(f"Count for 'Medicaid-doc': {count_2}")
print(f"Count for 'Private-ins-doc': {count_3}")

# %%
