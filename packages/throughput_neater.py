#!/usr/bin/env python3

# Import basic modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
import scipy.stats
import seaborn as sns

# Set seaborn graph styling
MAX_ROWS = 10
pd.set_option('display.max_rows', MAX_ROWS)
pd.set_option('display.max_columns', 200)
sns.set_style("whitegrid")
sns.set_context("paper")

# Load the dataframe from Excel file
def LoadDFThroughputFromExcel(file_source, index_col='Timestamp', columns_orig=['Device', 'XL Total Throughput Details'], columns_changed=['Device', 'Throughput']):
    # Load into dataframe
    df = pd.read_excel(file_source, index_col='Timestamp')
    # Sort by index inplace
    df.sort_index(inplace=True)
    # Convert the timestamp to datetime type
    df.index = pd.to_datetime(df.index)
    # Filter columns to be used
    df = df[columns_orig]
    # Change column name
    df.columns = columns_changed
    # Return back the dataframe
    return df

# Function to Subset Dataframe Based on NodeName
def SubsetDFThroughput(df, nodename):
    return df[df['Device']==nodename]

# Graph all the nodes in a loop
def VisualizeTimeSeriesThroughput(df):
    for node in list(df['Device'].unique()):
        df_node = df[df['Device'] == node] # make a df for each node
        df_node.plot(grid=True, title=node)
        plt.ylabel('Throughput (Gbps)')
        plt.gcf().set_size_inches(17, 2.58, forward=True)
        plt.show()
        print('Maximum: ', df_node['Throughput'].max(), df_node[['Throughput']].idxmax(axis=0))
        print('Average: ', "%.2f" % df_node['Throughput'].mean())
        df_node.boxplot()
        plt.ylabel('Throughput (Gbps)')
        plt.title(node)
        plt.show()

# Function to visualize linear data
def VisualizeThroughputLinearData(df, title, ylabel='Throughput (Gbps)', xsize_inches=17, ysize_inches=2.58):
    # Line graph
    df.plot()
    plt.ylabel(ylabel)
    plt.gcf().set_size_inches(xsize_inches, ysize_inches, forward=True)
    plt.title(title)
    plt.show()

    # Box plot
    df.boxplot()
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()

    # Data description
    print(df.describe())

# VisualizeThroughputDensity draws line and boxplot graph
# logarithmic switch toggles if the graphs drawn are normal or logarithmized one
def VisualizeThroughputDensity(df, column_name='Throughput', kind='kde', coefficient=1.1, logarithmic=False):
    # Toggles graph type
    if logarithmic == True:
        i = 'Log_' + column_name
        df[i] = np.log(df[column_name])
    else:
        i = column_name

    # Line graph
    plt.figure(figsize=(10,8))
    plt.subplot(211)
    plt.xlim(df[i].min(), df[i].max()*coefficient)
    ax = df[i].plot(kind=kind)
    
    # Box Plot 
    plt.subplot(212)
    plt.xlim(df[i].min(), df[i].max()*coefficient)
    sns.boxplot(x=df[i])

# Find the peaks of the throughput
def FindThroughputPeaks(df):
    mean_throughput = df['Throughput'].mean()
    peaks, _ = scipy.signal.find_peaks(df['Throughput'],
        height=mean_throughput, threshold=None)
    plt.figure(figsize=(14,8))
    plt.plot_date(df.index, df['Throughput'],
             'b-', linewidth=2)
    plt.plot_date(df.index[peaks], df['Throughput'][peaks],
              'ro', label='positive peaks')
    plt.xlabel('Datetime')
    plt.ylabel('Throughput (Gbps)')
    plt.legend(loc=4)
    plt.show()
    
# Create a function to get the IQD value of the series
def TransformIQD(df, column_name='Throughput'):
    # Add one field of logarithmic-transformed value of the input column name
    df['Log_' + column_name] = np.log(df[column_name])
    # Get the quartiles
    q75, q25 = np.percentile(df['Log_' + column_name].dropna(), [75, 25])
    # Get the IQR value
    iqr = q75 - q25
    # Get the min and max of the IQR values
    min_log = q25 - (iqr * 1.5)
    max_log = q75 + (iqr * 1.5)
    # Add one field 'Outlier', set default value to 0
    df['Outlier'] = 0
    df.loc[df['Log_' + column_name] < min_log, 'Outlier'] = 1
    df.loc[df['Log_' + column_name] > max_log, 'Outlier'] = 1
    return df, min_log, max_log

# Function to remove outlier data
def RemoveOutliers(df):
    df = df[df['Outlier']==0]
    return df

# Create a fuction to visualize the graph with IQD parameters
def VisualizeIQDTransformation(df, min_log, max_log, column_name='Log_Throughput'):
    # Set the plot canvass for the first graph
    plt.figure(figsize=(10,8))
    plt.subplot(211)
    plt.xlim(df[column_name].min(), df[column_name].max()*1.1)
    plt.axvline(x=min_log)
    plt.axvline(x=max_log)
    # Plot the data
    ax = df[column_name].plot(kind='kde')
    # Set the plot canvass for the second graph
    plt.subplot(212)
    plt.xlim(df[column_name].min(), df[column_name].max()*1.1)
    # Plot the boxplot
    sns.boxplot(x=df[column_name])
    plt.axvline(x=min_log)
    plt.axvline(x=max_log)

# Create a function to get the MSD value of the series
def TransformMSD(df, column_name, coefficient=3):
    df_msd = df[np.abs(df[column_name]-df[column_name].mean()) <= (coefficient * df[column_name].std())]
    return df_msd


# CleanThroughputDataAndVisualize is a function to do all cleaning functions in one swoop.
# It accepts an excel file and will load the content into dataframe. 
# It will visualize all the data for visual checks
def CleanThroughputDataAndVisualize(file_excel):
    # Load the excel file
    df = LoadDFThroughputFromExcel(file_excel)
    # Visualize the original graph for all nodes
    VisualizeTimeSeriesThroughput(df)
    # Loop through each unique node name
    for node in list(df['Device'].unique()):
        # Subset each device into a dataframe
        df_node = SubsetDFThroughput(df, node)
        # Visualize linear representation of the throughput data for the node
        VisualizeThroughputLinearData(df_node, node)
        # Print the arithmetic description of the data
        print(df_node.describe())
        # Visualize the density representation of the throughput data for the node
        VisualizeThroughputDensity(df_node, logarithmic=False)
        # Visualize the logarithmic representation of the throughput data for the node
        VisualizeThroughputDensity(df_node, logarithmic=True)
        # IQD Transform the data, get the min and max logarithmic
        df_node, min_log_df, max_log_df = TransformIQD(df_node)
        # Visualize the data after IQD transformed
        VisualizeIQDTransformation(df_node, min_log_df, max_log_df)
        # Remove outliers from datarame 
        df_node = RemoveOutliers(df_node)
        # Visualize again the linear data after outliers are removed
        VisualizeThroughputLinearData(df_node, node)
        # Transform the data using MSD
        df_node = TransformMSD(df_node, 'Throughput', 3)
        # Visualize again
        VisualizeThroughputLinearData(df_node, node)

# CleanThroughputData is a function to do all cleaning functions in one swoop.
# It accepts an excel file and will load the content into dataframe. 
# It returns a dict of cleaned throughput dataframe for all nodes
def CleanThroughputData(file_excel):
    # Load the excel file
    df = LoadDFThroughputFromExcel(file_excel)
    # Create a df_dict {'NodeName': df_node}
    df_dict = {}
    # Loop through each unique node name
    for node in list(df['Device'].unique()):
        # Subset each device into a dataframe
        df_node = SubsetDFThroughput(df, node)
        # Use IQD method to transform the data, get the min and max logarithmic
        df_node, min_log_df, max_log_df = TransformIQD(df_node)
        # Remove outliers from dataframe
        df_node = RemoveOutliers(df_node)
        # Use MSD method to transform the data
        df_node = TransformMSD(df_node, 'Throughput', 3)
        # Assign to df_dict
        df_dict[node] = df_node
    return df_dict

# ConstructThroughputTable is a function which accepts a dictionary of cleaned dataframe
# and a dictionary of nodes:upper_limit_capacity. It uses both arguments and will return
# a dataframe of summarized throughput utilization
def ConstructThroughputTable(df_dict, node_tput_cap_dict):
    throughput_table = pd.DataFrame(index=sorted(list(df_dict.keys())),
        columns = ['Peak (Mbps)', 'Average (Mbps)', 'Busiest Day'])
    tput_cap_table = pd.DataFrame(node_tput_cap_dict.items(), columns=['Device', 'Capacity (Mbps)'])
    tput_cap_table.set_index('Device', drop=True, inplace=True)
    throughput_table.index.name = 'Device'
    for node, df in df_dict.items():
        # locate the highest throughput in the data for each node, assign to Peak (Mbps)
        throughput_table.loc[node, 'Peak (Mbps)'] = int(df['Throughput'].max() * 1000)
        # calculate the average throughput in the data for each node, assign to Average (Mbps)
        throughput_table.loc[node, 'Average (Mbps)'] = int(df['Throughput'].mean() * 1000)
        # locate the date where it has the highest throughput
        throughput_table.loc[node, 'Busiest Day'] = df['Throughput'].idxmax(axis=0).date() 
    # Concat the throughput and node throughput cap dataframe
    df = pd.concat([throughput_table, tput_cap_table], axis=1)
    # Append a totals row
    df = df.append(pd.DataFrame({\
            'Capacity (Mbps)':tput_cap_table.loc[:,'Capacity (Mbps)'].sum(),\
            'Peak (Mbps)':throughput_table.loc[:,'Peak (Mbps)'].sum(),\
            'Average (Mbps)':throughput_table.loc[:,'Average (Mbps)'].sum()},index=['TOTAL']))
    # Calculate the peak percentage against capacity
    df['Peak Utilization (%)'] = (df['Peak (Mbps)'] / df['Capacity (Mbps)']) * 100
    df['Peak Utilization (%)'] = df['Peak Utilization (%)'].apply(lambda x: np.round(x, decimals=2))
    # Calculate the mean percentage against capacity
    df['Mean Utilization (%)'] = (df['Average (Mbps)'] / df['Capacity (Mbps)']) * 100
    df['Mean Utilization (%)'] = df['Mean Utilization (%)'].apply(lambda x: np.round(x, decimals=2))
    # Handle NaN in Busiest Day: change to blank
    df = df.fillna('')
    return df

# Define a map of committed throughput capacity for each GGSN
tputcap = {'GGBNB01':66000,
           'GGBNB02':66000,
           'GGCBT11':94000,
           'GGCBT12':94000,
           'GGCBT13':94000,
           'GGCBT14':39000,
           'GGCBT15':94000,
           'GGCBT16':55000,
           'GGCBT17':94000,
           'GGCBT18':94000,
           'GGCBT05':10000,
}