#%%

import pandas as pd

# Load the CSV file with a specified encoding and handle bad lines
file_path = '/Users/dannyzweben/Desktop/CAADC/Table Creation/hdtchart.csv'
pmaxe = pd.read_csv(file_path)
# Display the DataFrame
print(pmaxe.head())






# %%
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import docx
from docx.shared import Inches
from scipy.stats import median_abs_deviation

# Load your actual DataFrame (Ensure 'pmaxe' is defined)
# pmaxe = pd.read_csv("your_data.csv")  # Uncomment if loading from a CSV

# Ensure 'Pmax' column is numeric and remove invalid values
for col in ["1st trial (Non-Doctoral Providers)", "2nd trail (Non-Doctoral Providers)"]:
    pmaxe[col] = pd.to_numeric(pmaxe[col], errors="coerce")  # Convert non-numeric to NaN

# Melt the DataFrame into long format
pmaxe_melted = pmaxe.melt(
    value_vars=["1st trial (Non-Doctoral Providers)", "2nd trail (Non-Doctoral Providers)"],
    var_name="Condition",
    value_name="Pmax"
)

# Rename categories for clarity
condition_mapping = {
    "1st trial (Non-Doctoral Providers)": "Without\nAdmin\nAssistance",
    "2nd trail (Non-Doctoral Providers)": "With\nAdmin\nAssistance"
}
pmaxe_melted["Condition"] = pmaxe_melted["Condition"].map(condition_mapping)

# Drop NaN values (ensures medians and CI calculations work)
pmaxe_melted = pmaxe_melted.dropna()

# Check for missing data
print("Missing values per column:\n", pmaxe_melted.isnull().sum())

# Initialize figure
fig, ax = plt.subplots(figsize=(5, 7))

# Scatter plot (jitter applied manually)
sns.stripplot(
    x="Condition", y="Pmax", data=pmaxe_melted, jitter=False, dodge=False, alpha=0.6,
    edgecolor="black", linewidth=0.7, color="white", marker="o", zorder=3,
    order=["Without\nAdmin\nAssistance", "With\nAdmin\nAssistance"]
)

# Apply manual jitter for better spread while maintaining correct x-centers
jitter_strength = 0.04
for i, category in enumerate(["Without\nAdmin\nAssistance", "With\nAdmin\nAssistance"]):
    subset = pmaxe_melted[pmaxe_melted["Condition"] == category]
    n_points = len(subset)
    jitter_x = np.random.uniform(-jitter_strength, jitter_strength, n_points)
    adjusted_x_positions = np.full(n_points, [0.2, 0.6][i]) + jitter_x
    y_positions = subset["Pmax"].values
    ax.collections[i].set_offsets(np.c_[adjusted_x_positions, y_positions])

# Ensure x-axis line appears behind the dots
ax.axhline(y=0, color='black', linewidth=1, zorder=1)
ax.spines["bottom"].set_visible(False)

# Compute and plot median + 95% confidence intervals
conditions = ["Without\nAdmin\nAssistance", "With\nAdmin\nAssistance"]
for i, cond in enumerate(conditions):
    values = pmaxe_melted[pmaxe_melted["Condition"] == cond]["Pmax"].dropna()
    if values.empty:
        print(f"WARNING: No valid data for condition '{cond}'")
        continue  # Skip if there's no data

    median_val = np.median(values)
    ci_95 = 1.96 * median_abs_deviation(values) / np.sqrt(len(values))  # Confidence interval

    # Debugging printout
    print(f"{cond} Median: {median_val}, CI Lower: {median_val - ci_95}, CI Upper: {median_val + ci_95}")

    # Get x position
    x_pos = [0.2, 0.6][i]

    # Plot median bar
    ax.hlines(median_val, x_pos - 0.05, x_pos + 0.05, color="black", linewidth=3, zorder=4)

    # Plot 95% CI vertical line
    ax.vlines(x_pos, median_val - ci_95, median_val + ci_95, color="black", linewidth=1.5, zorder=4)

    # Plot horizontal caps for confidence intervals
    ax.hlines(median_val - ci_95, x_pos - 0.04, x_pos + 0.04, color="black", linewidth=1.5, zorder=4)
    ax.hlines(median_val + ci_95, x_pos - 0.04, x_pos + 0.04, color="black", linewidth=1.5, zorder=4)

# Set y-scale and labels
ax.set_ylim(-10, 500)
ax.set_yticks([0, 100, 200, 300, 400, 500])
ax.set_ylabel("Pmax", fontsize=14)

# Adjust x-axis category spacing
ax.set_xlabel("")
ax.set_xticks([0.2, 0.6])
ax.set_xticklabels(["Without\nAdmin\nAssistance", "With\nAdmin\nAssistance"], fontsize=12)

# Remove top and right spines (borders)
ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)

# Improve layout
plt.tight_layout()

# Save plot as an image
fig.savefig("pmax_chart.png", dpi=300)

# Export to Word document
doc = docx.Document()
doc.add_heading("Pmax Comparison Chart", level=1)
doc.add_picture("pmax_chart.png", width=Inches(5))
doc.save("pmax_chart.docx")

# Show plot
plt.show()

# %%







### Violin Plots





# %%
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import docx
from docx.shared import Inches
from scipy.stats import median_abs_deviation

# Load your actual DataFrame (Ensure 'pmaxe' is defined)
# pmaxe = pd.read_csv("your_data.csv")  # Uncomment if loading from a CSV

# Ensure 'Pmax' column is numeric and remove invalid values
for col in ["1st trial (Non-Doctoral Providers)", "2nd trail (Non-Doctoral Providers)"]:
    pmaxe[col] = pd.to_numeric(pmaxe[col], errors="coerce")  # Convert non-numeric to NaN

# Melt the DataFrame into long format
pmaxe_melted = pmaxe.melt(
    value_vars=["1st trial (Non-Doctoral Providers)", "2nd trail (Non-Doctoral Providers)"],
    var_name="Condition",
    value_name="Pmax"
)

# Rename categories for clarity
condition_mapping = {
    "1st trial (Non-Doctoral Providers)": "Without\nAdmin\nAssistance",
    "2nd trail (Non-Doctoral Providers)": "With\nAdmin\nAssistance"
}
pmaxe_melted["Condition"] = pmaxe_melted["Condition"].map(condition_mapping)

# Drop NaN values
pmaxe_melted = pmaxe_melted.dropna()

# Check for missing data
print("Missing values per column:\n", pmaxe_melted.isnull().sum())

# Initialize figure
fig, ax = plt.subplots(figsize=(5, 7))

# Define colors for the violin plots
violin_colors = ["gray", "lightgray"]

# Create a violin plot with customized colors
violin_parts = sns.violinplot(
    x="Condition", y="Pmax", data=pmaxe_melted, inner=None, 
    cut=0, linewidth=1.2, width=0.8, scale="width", ax=ax,
    palette=violin_colors
)

# Extract violin widths dynamically
conditions = list(condition_mapping.values())

for i, violin in enumerate(ax.collections[:2]):  # The first two collections are the violins
    paths = violin.get_paths()
    max_x = max([p.vertices[:, 0].max() for p in paths])  # Get max width of the violin
    min_x = min([p.vertices[:, 0].min() for p in paths])  # Get min width of the violin
    violin_width = (max_x - min_x) / 2  # Half-width for centering

    # Compute and plot median + 95% confidence intervals
    cond = conditions[i]
    values = pmaxe_melted[pmaxe_melted["Condition"] == cond]["Pmax"].dropna()
    if values.empty:
        print(f"WARNING: No valid data for condition '{cond}'")
        continue  # Skip if there's no data

    median_val = np.median(values)
    q1_val = np.percentile(values, 25)  # 25th percentile (Q1)
    q3_val = np.percentile(values, 75)  # 75th percentile (Q3)
    ci_95 = 1.96 * median_abs_deviation(values) / np.sqrt(len(values))  # Confidence interval

    # Debugging printout
    print(f"{cond} Median: {median_val}, Q1: {q1_val}, Q3: {q3_val}, CI Lower: {median_val - ci_95}, CI Upper: {median_val + ci_95}")

    # Get x position
    x_pos = i  # Violin plot uses index positions

    # **Thinner Median Line**
    ax.hlines(median_val, x_pos - violin_width, x_pos + violin_width, color="black", linewidth=1.5, zorder=4)

    # **Shorter & Thinner Confidence Interval (CI) Lines**
    ci_width = violin_width * 0.4  # Shorter than the median line
    ax.hlines(median_val - ci_95, x_pos - ci_width, x_pos + ci_width, color="black", linewidth=0.8, zorder=4)  # Lower CI
    ax.hlines(median_val + ci_95, x_pos - ci_width, x_pos + ci_width, color="black", linewidth=0.8, zorder=4)  # Upper CI

    # **Thinner Quartile Lines (Q1 & Q3)**
    ax.hlines(q1_val, x_pos - violin_width, x_pos + violin_width, color="black", linewidth=1.2, linestyle="dotted", zorder=4)  # Q1
    ax.hlines(q3_val, x_pos - violin_width, x_pos + violin_width, color="black", linewidth=1.2, linestyle="dotted", zorder=4)  # Q3

    # **Thinner Vertical CI Line**
    ax.vlines(x_pos, median_val - ci_95, median_val + ci_95, color="black", linewidth=1, zorder=4)

    # **Plot Median Marker (Black Dot)**
    ax.scatter(x_pos, median_val, color="black", zorder=5, s=50, marker="o")

# **Overlay individual data points as faded white bubbles with slightly thicker black outlines**
sns.stripplot(
    x="Condition", y="Pmax", data=pmaxe_melted, 
    color="white", alpha=0.4, edgecolor="black", linewidth=1, size=6, jitter=0.11, dodge=True,
    zorder=2  # Lower than CI bars & median
)

# Set y-scale and labels
ax.set_ylim(-10, 500)
ax.set_yticks([0, 100, 200, 300, 400, 500])
ax.set_ylabel("Pmax", fontsize=14)

# Add minor tick marks (every 25 units) without extending gridlines
ax.yaxis.set_minor_locator(plt.MultipleLocator(25))
ax.tick_params(axis="y", which="minor", length=4, color="black", width=1)

# Adjust x-axis category spacing
ax.set_xlabel("")
ax.set_xticks(range(len(conditions)))
ax.set_xticklabels(conditions, fontsize=12)

# Remove top and right spines (borders)
ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)

# Improve layout
plt.tight_layout()

# Save plot as an image
fig.savefig("pmax_chart_violin.png", dpi=300)

# Export to Word document
doc = docx.Document()
doc.add_heading("Pmax Comparison Chart (Violin Plot)", level=1)
doc.add_picture("pmax_chart_violin.png", width=Inches(5))
doc.save("pmax_chart_violin.docx")

# Show plot
plt.show()
# %%




############### RUN AGAIN FOR PHD PROVIDERS #####################

# %%
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import docx
from docx.shared import Inches
from scipy.stats import median_abs_deviation

# Load your actual DataFrame (Ensure 'pmaxe' is defined)
# pmaxe = pd.read_csv("your_data.csv")  # Uncomment if loading from a CSV

# Ensure 'Pmax' column is numeric and remove invalid values
for col in ["1st trial (Doctoral Providers)", "2nd trial (Doctoral Providers)"]:
    pmaxe[col] = pd.to_numeric(pmaxe[col], errors="coerce")  # Convert non-numeric to NaN

# Melt the DataFrame into long format
pmaxe_melted = pmaxe.melt(
    value_vars=["1st trial (Doctoral Providers)", "2nd trial (Doctoral Providers)"],
    var_name="Condition",
    value_name="Pmax"
)

# Rename categories for clarity
condition_mapping = {
    "1st trial (Doctoral Providers)": "Without\nAdmin\nAssistance",
    "2nd trial (Doctoral Providers)": "With\nAdmin\nAssistance"
}
pmaxe_melted["Condition"] = pmaxe_melted["Condition"].map(condition_mapping)

# Drop NaN values
pmaxe_melted = pmaxe_melted.dropna()

# Check for missing data
print("Missing values per column:\n", pmaxe_melted.isnull().sum())

# Initialize figure
fig, ax = plt.subplots(figsize=(5, 7))

# Define colors for the violin plots
violin_colors = ["gray", "lightgray"]

# Create a violin plot with customized colors
violin_parts = sns.violinplot(
    x="Condition", y="Pmax", data=pmaxe_melted, inner=None, 
    cut=0, linewidth=1.2, width=0.8, scale="width", ax=ax,
    palette=violin_colors
)

# Extract violin widths dynamically
conditions = list(condition_mapping.values())

for i, violin in enumerate(ax.collections[:2]):  # The first two collections are the violins
    paths = violin.get_paths()
    max_x = max([p.vertices[:, 0].max() for p in paths])  # Get max width of the violin
    min_x = min([p.vertices[:, 0].min() for p in paths])  # Get min width of the violin
    violin_width = (max_x - min_x) / 2  # Half-width for centering

    # Compute and plot median + 95% confidence intervals
    cond = conditions[i]
    values = pmaxe_melted[pmaxe_melted["Condition"] == cond]["Pmax"].dropna()
    if values.empty:
        print(f"WARNING: No valid data for condition '{cond}'")
        continue  # Skip if there's no data

    median_val = np.median(values)
    q1_val = np.percentile(values, 25)  # 25th percentile (Q1)
    q3_val = np.percentile(values, 75)  # 75th percentile (Q3)
    ci_95 = 1.96 * median_abs_deviation(values) / np.sqrt(len(values))  # Confidence interval

    # Debugging printout
    print(f"{cond} Median: {median_val}, Q1: {q1_val}, Q3: {q3_val}, CI Lower: {median_val - ci_95}, CI Upper: {median_val + ci_95}")

    # Get x position
    x_pos = i  # Violin plot uses index positions

    # **Thinner Median Line**
    ax.hlines(median_val, x_pos - violin_width, x_pos + violin_width, color="black", linewidth=1.5, zorder=4)

    # **Shorter & Thinner Confidence Interval (CI) Lines**
    ci_width = violin_width * 0.4  # Shorter than the median line
    ax.hlines(median_val - ci_95, x_pos - ci_width, x_pos + ci_width, color="black", linewidth=0.8, zorder=4)  # Lower CI
    ax.hlines(median_val + ci_95, x_pos - ci_width, x_pos + ci_width, color="black", linewidth=0.8, zorder=4)  # Upper CI

    # **Thinner Quartile Lines (Q1 & Q3)**
    ax.hlines(q1_val, x_pos - violin_width, x_pos + violin_width, color="black", linewidth=1.2, linestyle="dotted", zorder=4)  # Q1
    ax.hlines(q3_val, x_pos - violin_width, x_pos + violin_width, color="black", linewidth=1.2, linestyle="dotted", zorder=4)  # Q3

    # **Thinner Vertical CI Line**
    ax.vlines(x_pos, median_val - ci_95, median_val + ci_95, color="black", linewidth=1, zorder=4)

    # **Plot Median Marker (Black Dot)**
    ax.scatter(x_pos, median_val, color="black", zorder=5, s=50, marker="o")

# **Overlay individual data points as faded white bubbles with slightly thicker black outlines**
sns.stripplot(
    x="Condition", y="Pmax", data=pmaxe_melted, 
    color="white", alpha=0.4, edgecolor="black", linewidth=1, size=6, jitter=0.11, dodge=True,
    zorder=2  # Lower than CI bars & median
)

# Set y-scale and labels
ax.set_ylim(-10, 500)
ax.set_yticks([0, 100, 200, 300, 400, 500])
ax.set_ylabel("Pmax", fontsize=14)

# Add minor tick marks (every 25 units) without extending gridlines
ax.yaxis.set_minor_locator(plt.MultipleLocator(25))
ax.tick_params(axis="y", which="minor", length=4, color="black", width=1)

# Adjust x-axis category spacing
ax.set_xlabel("")
ax.set_xticks(range(len(conditions)))
ax.set_xticklabels(conditions, fontsize=12)

# Remove top and right spines (borders)
ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)

# Improve layout
plt.tight_layout()

# Save plot as an image
fig.savefig("pmax_chart_violin_doct.png", dpi=300)

# Export to Word document
doc = docx.Document()
doc.add_heading("Pmax Comparison Chart (Violin Plot)", level=1)
doc.add_picture("pmax_chart_violin_doct.png", width=Inches(5))
doc.save("pmax_chart_violin.docx")

# Show plot
plt.show()
# %%
