#!/bin/bash

# Script Start Timing
start=$(date +%s)

# Get time variable
year=$(date +%Y)
last_month=$(date -d "last month" '+%m')
today=$(date +%Y%m%d)

# Set global vars : START, END flags, Core binary, Working Directory of the Core binary
START=""
END=""
SCRIPT=${HOME}/epc-capacity-monitoring/main
WORKDIR=${HOME}/epc-capacity-monitoring
CONFDIR=${HOME}/epc-capacity-monitoring/configs

# Set global vars : Post-processing script, directory ; Destination directory
DATA_NEATER=${HOME}/epc-capacity-monitoring/main.py
POST_PROC_DIR=${HOME}/epc-capacity-monitoring/processed
DEST_DIR=${POST_PROC_DIR}/${year}/${last_month}

# Check if destination directory exist
if [ ! -d ${DEST_DIR} ]; then
    mkdir -pv ${DEST_DIR}
else
    echo "Destination directory exists at ${DEST_DIR}"
fi

function call_sgsn() {
    # Script start timing
    start=$(date +%s)

    # Begin main function
    echo "Executing for SGSN"
    for i in $(cat ${CONFDIR}/nodelist/sgsn.txt); do
        IP=${i%,*};
        NAME=${i#*,};
        $SCRIPT --start=${START} --end=${END} --node=${IP} --nodename=${NAME} --resource="CPU_Load"
        $SCRIPT --start=${START} --end=${END} --node=${IP} --nodename=${NAME} --resource="SAU_2G3G"
        $SCRIPT --start=${START} --end=${END} --node=${IP} --nodename=${NAME} --resource="SAU_4G"
    done

    # Finish flag for SGSN
    echo "Moving SGSN PM data to ${WORKDIR}/sgsn"
    mv ${WORKDIR}/*.csv ${WORKDIR}/sgsn
    echo "Done executing script for SGSN"

    # Script end timing
    end=$(date +%s)
    runtime=$((end-start))
    echo "SGSN PM data caller done execution in ${runtime} seconds"
}

function call_ggsn() {
    # Script start timing
    start=$(date +%s)

    # Begin main function
    echo "Executing for GGSN"
    for i in $(cat ${CONFDIR}/nodelist/ggsn.txt); do
        IP=${i%,*};
        NAME=${i#*,};
        $SCRIPT --start=${START} --end=${END} --node=${IP} --nodename=${NAME} --resource="GGSN_IP_Pool"
        $SCRIPT --start=${START} --end=${END} --node=${IP} --nodename=${NAME} --resource="CPU_Load"
        $SCRIPT --start=${START} --end=${END} --node=${IP} --nodename=${NAME} --resource="GGSN_Session"
    done

    # Since GGSN TPUT resource call will get the data for all GGSNs
    # ...move the invocation outside the for loop
    echo "Calling GGSN throughput data bundle"
    $SCRIPT --start=${START} --end=${END} --resource="GGSN_Tput"

    # Finish flag for GGSN
    echo "Moving GGSN PM data to ${WORKDIR}/ggsn"
    mv ${WORKDIR}/*.csv ${WORKDIR}/ggsn
    echo "Done executing script for GGSN"

    # Script end timing
    end=$(date +%s)
    runtime=$((end-start))
    echo "GGSN PM data caller done execution in ${runtime} seconds"
}

# check if current year is leap year
current_year=$(date +%Y)
leap=""
leap_check=$((current_year % 4))

if [ $leap_check -eq 0 ]; then
    leap=29
else
    leap=28
fi

# bash 4 has associative array
# declare array of end date of month in a year
declare -A calendar
calendar["Jan"]=31
calendar["Feb"]=${leap}
calendar["Mar"]=31
calendar["Apr"]=30
calendar["May"]=31
calendar["Jun"]=30
calendar["Jul"]=31
calendar["Aug"]=31
calendar["Sep"]=30
calendar["Oct"]=31
calendar["Nov"]=30
calendar["Dec"]=31

# Check for current month
current_month=$(date +%m)

# start_month : two months back from 15th day of running month
# end_month : one month back from 15th day of running month
#start_month=$(date --date="$(date +%Y-%m-15) -2 month" +%m)
#start_month=$(date --date="$(date +%Y-%m-15) -1 month" +%m)
start_month=$(date -d "2 months ago" +%m)
#end_month=$(date --date="$(date +%Y-%m-15) -1 month" +%m)
#end_month=$(date --date="$(date +%Y-%m-15)" +%m)
end_month=$(date -d "1 month ago" +%m)
#start_month_string=$(date --date="$(date +%Y-%m-15) -2 month" +%b)
start_month_string=$(date -d "2 months ago" +%b)
#end_month_string=$(date --date="$(date +%Y-%m-15) -1 month" +%b)
end_month_string=$(date -d "1 month ago" +%b)
start_year=""
end_year=""
start_month_last_date=""
end_month_last_date=""

if [ $current_month -eq 01 ]; then
    # do something
    start_year=$(date -d "1 year ago" '+%Y')
    end_year=$(date -d "1 year ago" '+%Y')
    start_month_last_date=${calendar[${start_month_string}]}
    end_month_last_date=${calendar[${end_month_string}]}
else
    # do something
    start_year=$(date '+%Y')
    end_year=$(date '+%Y')
    start_month_last_date=${calendar[${start_month_string}]}
    end_month_last_date=${calendar[${end_month_string}]}   
fi

START=${start_year}-${start_month}-${start_month_last_date} 
END=${end_year}-${end_month}-${end_month_last_date}

# Print fancy banner
cat << EOF
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    @      EPC Capacity Monitoring Collector Scripts    @
    @      Copyright  : Ngakan Nyoman Gandhi            @
    @      Start Date : ${START}                        @
    @      END DATE   : ${END}                          @
    @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    Send inquiries to <ngakan.gandhi@packet-systems.com>
EOF

# Call the csv gatherer scripts
printf "Running SGSN data gatherer...start date: %s, end date: %s \n" ${START} ${END} ; call_sgsn
printf "Running GGSN data gatherer...start date: %s, end date: %s \n" ${START} ${END} ; call_ggsn

# Call the data neater scripts
echo "Running data neater script..." ; $DATA_NEATER

## Final cleanups
# 1. Moving the processed file into destination directory
echo "moving post-processed XLS file into cold storage directory"
mv ${POST_PROC_DIR}/*xls ${DEST_DIR}

# 2. Moving the raw file into separate directory
# a. SGSN
cold_csv_dir_sgsn=${WORKDIR}/sgsn/${today}

# Check if destination directory exist
if [ ! -d ${cold_csv_dir_sgsn} ]; then
    mkdir -pv ${cold_csv_dir_sgsn}
else
    echo "Destination directory exists at ${cold_csv_dir_sgsn}"
fi
echo "moving SGSN raw files into cold storage directory"
mv ${WORKDIR}/sgsn/*.csv ${cold_csv_dir_sgsn}

# b. GGSN
cold_csv_dir_ggsn=${WORKDIR}/ggsn/${today}

# Check if destination directory exist
if [ ! -d ${cold_csv_dir_ggsn} ]; then
    mkdir -pv ${cold_csv_dir_ggsn}
else
    echo "Destination directory exists at ${cold_csv_dir_ggsn}"
fi
echo "moving GGSN raw files into cold storage directory"
mv ${WORKDIR}/ggsn/*.csv ${cold_csv_dir_ggsn}

# Flag off
echo "Done!"