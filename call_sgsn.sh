#!/usr/bin/bash

# Script Start Timing
start=$(date +%s)

# Set global vars
START=$1
END=$2
SCRIPT=/home/psi/go/CapMon/CapMon
WORKDIR=/home/psi/go/CapMon

# CLI args helper
if [ $# -lt 2 ]; then
    echo "Please provide command-line arguments"
    echo "Example: $0 2019-03-01 2019-03-31"
    exit 1
fi

## Main
# SGSN
echo "Executing for SGSN"
for i in $(cat ${WORKDIR}/sgsn.txt); do
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

# Script End Timing
end=$(date +%s)
runtime=$((end-start))
echo "Script done execution in ${runtime} seconds"