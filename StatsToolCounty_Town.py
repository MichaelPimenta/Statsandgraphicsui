import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Load your data
# data = pd.read_csv('D:\\CIRCA\\CTEJIndex_v1_4_2\\output.csv')
file_path = 'output.csv'

# Select either town or county
level = st.selectbox('Select level', ('TOWN_NAME', 'County'))

# Create multiselect widget for towns or counties
options = list(data[level].unique())
options.sort()  # Sort the town/county names alphabetically
selected = st.multiselect(f'Select {level}(s)', ['Select All'] + options)

# Check for 'Select All' in the selection
if 'Select All' in selected:
    selected = options[1:]  # Select all options except the 'Select All' option

# Filter DataFrame based on user's selection
filtered_data = data[data[level].isin(selected)]
st.write("Note: Very small towns with only one data point will not have extensive statistics performed on them, as there is no meaningful analysis to be done with only one data point.")
# Display the filtered data in the Streamlit app
st.write(filtered_data)

# Columns to calculate statistics on
stat_columns = [
    'Area_SqMil', 'Area_Sqft', 'Area_SqM', 'HealthSens', 'SocioEcoFa', 'SensitiveP', 
    'PollExposu', 'PollSource', 'PollutionB', 'Score', 'Percentile', 'Rank', 'TotalPopul', 
    'PercentBla', 'PercentAme', 'PercentAsi', 'PercentNat', 'PercentOth', 'PercentHis', 
    'PercentWhi', 'TotalPerce', 'Unemployed', 'PovertyPer', 'Median_Inc'
]

# Exclude negative values from numerical columns
filtered_data_numeric = filtered_data[stat_columns]
filtered_data[filtered_data_numeric.columns] = filtered_data_numeric[filtered_data_numeric >= 0]

# Calculate descriptive statistics
stats = filtered_data[stat_columns].describe()

# Checkbox to select download option
separate_files = st.checkbox('Download Separately (Each County/Town in its Own Folder)')

# Check if there's only one selected county/town
is_single_selection = len(selected) == 1

# Create a layout with two columns
col1, col2 = st.columns(2)

# Display the "Select All" checkbox on top
if 'Select All' in selected:
    selected.remove('Select All')
    selected.insert(0, 'Select All')

# Display the "Display Statistics" button in the left column
if col1.button('Show Statistics'):
    # Display the calculated statistics in the Streamlit app
    col1.write(stats)

# Display the "Save Output" button in the right column
if col2.button('Save Output'):
    # Generate the filename based on the user's selection
    # Replace spaces with underscores in the selected town or county names
    selected_with_underscores = [s.replace(' ', '_') for s in selected]

    if separate_files or is_single_selection:
        # Create a new directory for each selected county/town
        for selection in selected:
            selection_with_underscores = selection.replace(' ', '_')
            output_dir = os.path.join(os.path.expanduser('~\\Downloads'), selection_with_underscores)
            os.makedirs(output_dir, exist_ok=True)

            # Filter the data for the individual county/town
            individual_data = filtered_data[filtered_data[level] == selection]

            # Export the data to a CSV file with the town/county name
            output_filename = f'{selection_with_underscores}.csv'
            output_path = os.path.join(output_dir, output_filename)
            individual_data.to_csv(output_path, index=False)

            if len(individual_data) > 1:
                # Export the descriptive statistics to a separate CSV file
                individual_stats = individual_data[stat_columns].describe()
                individual_stats_output_path = os.path.join(output_dir, f'{selection_with_underscores}_statistics.csv')
                individual_stats.to_csv(individual_stats_output_path)

                # Create and save the unsorted correlation matrix heatmap
                corr_matrix = individual_data[stat_columns].corr().fillna(0)  # Fill NaN values with zeros
                plt.figure(figsize=(10, 8))
                sns.heatmap(corr_matrix, annot=False, fmt=".2f", cmap='coolwarm_r', cbar=True)
                plt.title(f'Correlation Matrix Heatmap ({selection})')
                corr_matrix_output_path = os.path.join(output_dir, f'{selection_with_underscores}_correlation_matrix_heatmap.png')
                plt.savefig(corr_matrix_output_path)
                plt.close()

                # Additional visualization: Box Plots
                for column in filtered_data_numeric.columns:
                    plt.figure(figsize=(8, 6))
                    sns.boxplot(x=column, data=individual_data)
                    plt.xlabel(column)
                    plt.ylabel('Value')
                    plt.title(f'Box Plot of {column} ({selection})')
                    boxplot_output_path = os.path.join(output_dir, f'{selection_with_underscores}_{column}_boxplot.png')
                    plt.savefig(boxplot_output_path)
                    plt.close()

    else:
        # Export the statistics to a single CSV file
        output_filename = '_'.join(selected_with_underscores) + '.csv'
        output_path = os.path.join(os.path.expanduser('~\\Downloads'), output_filename)
        stats.to_csv(output_path, index=False)
        col2.write(f'Statistics saved to: {output_path}')
