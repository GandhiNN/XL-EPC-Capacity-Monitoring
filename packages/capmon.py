#!/usr/bin/env python3

# Import modules
import datetime
import glob
import json
import logging
import os
import sys
import numpy as np
import pandas as pd
import subprocess

# WriteGGSNActSession accepts a writer object, the raw csv file data, and the node name
def WriteGGSNActSession(resource_list_name, output_filename, node_json):
    # Load JSON file
    with open(node_json) as json_file:
        data = json.load(json_file)
    # Start logging and load raw file into dataframe
    with pd.ExcelWriter(output_filename) as writer:
        for d in data:
            logging.info("processing for %s, node = '%s'", output_filename, d['NodeName'])
            epc_node_csv = "".join([s for s in resource_list_name if d['NodeName'] in s])
            cols = ['APN Name', 'APN Total Active Bearers']
            apns = ['axis','axismms','blackberry.net','internet','www.xlgprs.net','www.xlmms.net','xlunlimited']
            df = pd.read_csv(epc_node_csv, index_col='Timestamp')
            # Select only relatable columns
            df = df[cols]
            # Select only rows whose column values matching apn list `apns`
            df = df[df['APN Name'].isin(apns)]
            # Convert columns:APN Total Active Bearers to float
            df['APN Total Active Bearers'] = df['APN Total Active Bearers'].str.replace(',','').astype(float)
            # Check for null values
            df = IsNull(df)
            # Group the dataframe and unstack to multiindex dataframe
            df = df.groupby(['Timestamp','APN Name']).sum().unstack()
            df.columns.set_levels(['APN Name'],level=0,inplace=True)
            logging.info("writing dataframe to excel sheet, sheet name='%s'", d['NodeName'])
            df.to_excel(writer, sheet_name=d['NodeName'])

# ConcatSAU is a function to concat dictionary of dataframes with the same key
def WriteSAUAllRAT(df1, df2, output_name):
    logging.info("concatenating dataframes...")
    df_dict = {k: pd.concat([df1[k], df2[k]]) for k in df1} 
    # Write to excel file into different sheets
    # one key (node name) per sheet
    with pd.ExcelWriter(output_name) as writer:
        for nodename, df in df_dict.items():
            logging.info("writing to spreadsheet %s for %s", output_name, nodename)
            df.to_excel(writer, sheet_name=nodename, index=False)
    writer.save()

# WriteGGSNTput is a function to write consolidated GGSN Throughput spreadsheet
def WriteGGSNTput(resource_list_name, output_filename):
    # Start logging and load raw file into dataframe
    logging.info("processing for %s", output_filename)
    epc_node_csv = "".join(resource_list_name)
    df = pd.read_csv(epc_node_csv)
    # Filter out unneeded columns
    cols = ['Device','Timestamp','XL Total Throughput Details','XL Total Uplink Traffic','XL Total Downlink Traffic']
    df = df[cols]
    # check for null values
    df = IsNull(df)
    # Format the timestamp
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y-%m-%dT%H:%M+0700')
    df['Timestamp'] = df['Timestamp'].dt.strftime('%m/%d/%Y %H:%M')
    # Filter out SGSN data
    sgsn = ['VSGBTR05','VSGBTR06','VSGCBT04','VSGCBT05']
    # Filter out rows containing values in sgsn under 'Device' column
    df = df[~df['Device'].isin(sgsn)] 
    # Write to excel file
    with pd.ExcelWriter(output_filename) as writer:
        sheet_name = 'Total Throughput Details'
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        writer.save()

# WriteNodeCPU is a function to write consolidated CPU load
# to a spreadsheet sans CF cards, Demux, and standby SF cards
def WriteNodeCPU(resource_list_name, output_filename, node_json):
    # Load JSON file
    with open(node_json) as json_file:
        data = json.load(json_file)
    # Start logging and load raw file into dataframe
    with pd.ExcelWriter(output_filename) as writer:
        for d in data:
            logging.info("processing for %s, node = '%s'", output_filename, d['NodeName'])
            epc_node_csv = "".join([s for s in resource_list_name if d['NodeName'] in s])
            # Load the data
            df = pd.read_csv(epc_node_csv)
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y-%m-%dT%H:%M+0700')
            # Group the dataframe and unstack to multiindex dataframe
            df = df.groupby(['Timestamp', 'Card ID']).sum()
            # Unstack the DF
            df = df.unstack()
            # Drop uppermost column level
            df.columns = df.columns.droplevel()
            # Select non-traffic serving cards to be excluded
            card_id_non_sf_active = d['CF'] + d['SFStandby'] + d['Demux']
            logging.info("dropping the following card with id: %s", str(card_id_non_sf_active).strip('[]'))
            # Drop the columns with card id = card_id_non_sf_active
            df_clean = df.drop(card_id_non_sf_active, axis=1)
            # Restack the dataframe (stack() returns a Series),
            # Reconvert to Dataframe, and rename the columns
            logging.info("reshaping the data to proper tabular format...")
            df_clean = df_clean.stack().to_frame().reset_index()
            df_clean.columns = ['Timestamp','Card ID','CPU Load Busy Percentage Last 5 Minutes Average']
            # Log for cleaned data : end result
            logging.info("writing dataframe to excel sheet, sheet name='%s'", d['NodeName'])
            df_clean.to_excel(writer, sheet_name=d['NodeName'], index=False)
        writer.save()

# WriteIPPool is a function to write consolidated
# GGSN IP Pool utilization to spreadsheet
def WriteIPPool(resource_list_name, output_filename, node_json):
    # Load JSON file
    with open(node_json) as json_file:
        data = json.load(json_file)
    # Write to excel file
    with pd.ExcelWriter(output_filename) as writer:
        for d in data:
            # Start logging and load raw file into dataframe
            logging.info("processing for %s, node = '%s'", output_filename, d['NodeName'])
            epc_node_csv = "".join([s for s in resource_list_name if d['NodeName'] in s])
            df = pd.read_csv(epc_node_csv)
            # Format the timestamp
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y-%m-%dT%H:%M+0700')
            df['Timestamp'] = df['Timestamp'].dt.strftime('%m/%d/%Y %H:%M')
            # Convert 'Number of IP Addresses Used' to float
            df['Number of IP Addresses Used'] = df['Number of IP Addresses Used'].str.replace(',','').astype(float)
            logging.info("writing dataframe to excel sheet, sheet name='%s'", d['NodeName'])
            df.to_excel(writer, sheet_name=d['NodeName'], index=False)
        writer.save()

# load_df_2g3g is a function to load 2G and 3G SAU into a dictionary of dataframe 
def LoadDf2g3gSAU(resource_list_name, node_list, output_filename):
    df_dict_2g_3g_sau = {}
    logging.info("processing for %s", output_filename)
    cols = ['VPN Name','VPN ID','Service Name','Timestamp','XL Overall SGSN 2G and 3G Attached Subscribers']
    for node in node_list:
        logging.info("loading %s csv to 2G-3G SAU dataframe", node)
        epc_node_csv = "".join([s for s in resource_list_name if node in s])
        df = pd.read_csv(epc_node_csv)
        # check for null values
        df = IsNull(df)
        df = df[cols]
        # rename column name
        df.rename(columns={'XL Overall SGSN 2G and 3G Attached Subscribers':'Attached Users'},inplace=True)
        # Convert 'Attach Users' to float
        df['Attached Users'] = df['Attached users'].str.replace(',','').astype(float)
        # Exclude rows with "map-svc"
        df = df[df['Service Name'] != "map-svc"]
        # Load to dict
        df_dict_2g_3g_sau[node] = df
    return df_dict_2g_3g_sau

# load_df_4g_sau is a function to load 4G SAU into a dictionary of dataframe
def LoadDF4GSau(resource_list_name, node_list, output_filename):
    df_dict_4g_sau = {}
    logging.info("processing for %s", output_filename)
    cols = ['VPN Name','VPN ID','Service Name','Timestamp','Attached Users']
    for node in node_list:
        logging.info("loading %s csv to 4G SAU dataframe", node)
        epc_node_csv = "".join([s for s in resource_list_name if node in s])
        df = pd.read_csv(epc_node_csv) 
        # check for null values
        df = IsNull(df)
        df = df[cols]
        # Convert 'Attached Users' to float
        df['Attached Users'] = df['Attached users'].str.replace(',','').astype(float)
        # Load to dict
        df_dict_4g_sau[node] = df
    return df_dict_4g_sau

# IsNull drops DF rows if containing NULL value
def IsNull(df):
    logging.info("checking for null data...")
    if df.isnull().values.any() == False:
        logging.info("there is no null data found")
        return df 
    else:
        rows_containing_null = df[df.isnull().any(axis=1)]
        logging.info("dropping null data found in \n", rows_containing_null)
        return df.dropna()

# SetLogging configures the logging level of our script
def SetLogging():
    # Set logging
    logging.basicConfig(format='%(asctime)s - %(message)s', 
        datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

# NodeCardMapper reads from static vEPC card mapping
# and converts to JSON format to be used by WriteNodeCPU
def NodeCardMapper(cwd, csvfile):
    # set the binary we want to execute
    binary = cwd + "/bin/node-cpu-mapper"
    logging.info("executing node cpu mapper...")
    subprocess.call([binary, csvfile])