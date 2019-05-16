#!/usr/bin/env python3

# Import modules
from packages.capmon import *

# SetVar is global setter for variables to be used in main
def SetVariables():
    today = datetime.date.today().strftime("%Y-%m-%d")
    cwd = os.path.dirname(os.path.realpath(__file__))
    ggsn_list = [
        'GGCBT11','GGCBT12','GGCBT13','GGCBT14','GGCBT15',
        'GGCBT16','GGCBT17','GGCBT18','GGBNB01','GGBNB02'
    ]
    sgsn_list = [
        'VSGBTR05', 'VSGCBT04', 'VSGCBT05', 'VSGBTR06'
    ]
    return today, cwd, ggsn_list, sgsn_list

# CreateDictOfFilenames returns dictionaries of ReportFilename as key
# RawData as values
def CreateDictOfFilenames(cwd, today):
    # Get ggsn resource list
    ggsn_cpu_list = glob.glob(cwd+"/ggsn/*CPU_Load*")
    ggsn_tput_list = glob.glob(cwd+"/ggsn/*GGSN_Tput*")
    ggsn_ippool_list = glob.glob(cwd+"/ggsn/*GGSN_IP_Pool*")
    ggsn_act_session_list = glob.glob(cwd+"/ggsn/*GGSN_Session*") 

    # Get sgsn resouce list
    sgsn_cpu_list = glob.glob(cwd+"/sgsn/*CPU_Load*")
    sgsn_2g3g_sau_list = glob.glob(cwd+"/sgsn/*SAU_2G3G*")
    sgsn_4g_sau_list = glob.glob(cwd+"/sgsn/*SAU_4G*")

    # Create variable for output filename
    GGSN_CPU_XLS = cwd + "/processed/GGSN CPU Load.xls"
    GGSN_TPUT_XLS = cwd + "/processed/GGSN Throughput.xls"
    GGSN_IP_POOL_XLS = cwd + "/processed/GGSN Number of IP Pool Used.xls"
    GGSN_ACT_SESSION_XLS = cwd + "/processed/GGSN-SAEGW PDP Session.xls"
    SGSN_CPU_XLS = cwd + "/processed/SGSN CPU Load.xls"
    SGSN_2G3G_SAU_XLS = cwd + "/processed/SGSN-2G-3G-SAU-" + today + ".xls"
    SGSN_4G_SAU_XLS = cwd + "/processed/SGSN-4G-SAU-" + today + ".xls"
    SGSN_TOTAL_SAU_XLS = cwd + "/processed/SGSN 2G 3G 4G SAU.xls"

    # Create dictionary of resources
    # key = filename, value = resource list
    output_filename_ggsn = {
        GGSN_CPU_XLS: ggsn_cpu_list,
        GGSN_TPUT_XLS: ggsn_tput_list,
        GGSN_IP_POOL_XLS: ggsn_ippool_list,
        GGSN_ACT_SESSION_XLS: ggsn_act_session_list
    }
    output_filename_sgsn = {
        SGSN_CPU_XLS: sgsn_cpu_list,
        SGSN_2G3G_SAU_XLS: sgsn_2g3g_sau_list,
        SGSN_4G_SAU_XLS: sgsn_4g_sau_list
    }
    return output_filename_ggsn, output_filename_sgsn

def main():
    # Set logger
    SetLogging()

    # Global variables getter
    today, cwd, ggsn_list, sgsn_list = SetVariables()

    # Set variable for SGSN total SAU excel file
    SGSN_TOTAL_SAU_XLS = cwd + "/processed/SGSN 2G 3G 4G SAU.xls"

    # Set variable for Node CPU CSV mapping
    saegw_csv = cwd + "/configs/cards/saegw-card-role.csv"
    sgsnmme_csv = cwd + "/configs/cards/sgsnmme-card-role.csv"

    # Get the dictionaries of filename vs raw data
    output_filename_ggsn, output_filename_sgsn = CreateDictOfFilenames(cwd, today)

    # Create the Node CPU mapping
    NodeCardMapper(cwd, saegw_csv)
    NodeCardMapper(cwd, sgsnmme_csv)

    # Set the name of the Node CPU JSON mapping
    saegw_json = cwd + "/configs/cards/saegw-card-role.json"
    sgsnmme_json = cwd + "/configs/cards/sgsnmme-card-role.json"

    # Loop through the dictionaries
    # SAEGW
    for k, v in output_filename_ggsn.items():
        if "Throughput" in k:
            WriteGGSNTput(v, k)
        elif "GGSN CPU" in k:
            WriteNodeCPU(v, k, saegw_json)
        elif "IP Pool" in k:
            WriteIPPool(v, k, saegw_json) 
        elif "PDP Session" in k:
            WriteGGSNPDPSession(v, k, saegw_json)
    # SGSNMME
    for k, v in output_filename_sgsn.items():
        if "SAU" in k:
            if "2G-3G-SAU" in k:
                df_2g3g_sau = LoadDf2g3gSAU(v, sgsn_list, k)
            elif "4G-SAU" in k:
                df_4g_sau = LoadDF4GSau(v, sgsn_list, k)
        elif "SGSN CPU" in k:
            WriteNodeCPU(v, k, sgsnmme_json)

    # Concatenate the SAU dataframes 
    WriteSAUAllRAT(df_4g_sau, df_2g3g_sau, SGSN_TOTAL_SAU_XLS)

if __name__ == "__main__":
    main()
