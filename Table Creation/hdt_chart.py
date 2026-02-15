#%%

import pandas as pd

# Load the CSV file with a specified encoding and handle bad lines
file_path = '/Users/dannyzweben/Desktop/CAADC/Table Creation/hdttable.csv'
hdtdata= pd.read_csv(file_path)
# Display the DataFrame
print(hdtdata.head())


#%%
from docx import Document
from docx.shared import Pt

# Create a Word document
doc = Document()
doc.add_heading('APA Table: HDT Results', 0)

# Add the table to the Word document
table = doc.add_table(rows=1, cols=len(hdtdata.columns))

# Adding the header row
hdr_cells = table.rows[0].cells
for i, column in enumerate(hdtdata.columns):
    hdr_cells[i].text = column

# Adding the data rows
for row in hdtdata.itertuples(index=False):
    row_cells = table.add_row().cells
    for i, value in enumerate(row):
        row_cells[i].text = str(value)

# Style the table to resemble an APA table (optional)
for cell in table._cells:
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.font.size = Pt(10)

# Save the Word document
doc.save('hdt-apa-table.docx')

print("APA table has been created and saved as 'hdt-apa-table.docx'")
# %%
import pandas as pd
from docx import Document
from docx.shared import Pt

# Load the CSV file
file_path = '/Users/dannyzweben/Desktop/CAADC/Table Creation/hdt-wtest.csv'
hdtdata = pd.read_csv(file_path)

# Display the DataFrame
print(hdtdata.head())

# Create a Word document
doc = Document()
doc.add_heading('APA Table: HDT WTest Results', 0)

# Add the table to the Word document
table = doc.add_table(rows=1, cols=len(hdtdata.columns))

# Adding the header row
hdr_cells = table.rows[0].cells
for i, column in enumerate(hdtdata.columns):
    hdr_cells[i].text = column

# Adding the data rows
for row in hdtdata.itertuples(index=False):
    row_cells = table.add_row().cells
    for i, value in enumerate(row):
        row_cells[i].text = str(value)

# Style the table to resemble an APA table (optional)
for cell in table._cells:
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            run.font.size = Pt(10)

# Save the Word document
doc.save('hdtwtest.docx')

print("APA table has been created and saved as 'hdtwtest.docx'")
# %%
