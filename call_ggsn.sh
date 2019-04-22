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
# GGSN
echo "Executing for GGSN"
for i in $(cat ${WORKDIR}/ggsn.txt); do
    IP=${i%,*};
    NAME=${i#*,};
    $SCRIPT --start=${START} --end=${END} --node=${IP} --nodename=${NAME} --resource="GGSN_IP_Pool"
    $SCRIPT --start=${START} --end=${END} --node=${IP} --nodename=${NAME} --resource="CPU_Load"
    $SCRIPT --start=${START} --end=${END} --node=${IP} --nodename=${NAME} --resource="GGSN_Session"
done

# Since GGSN TPUT resource call will get the data for all GGSNs
# ..move the invocation outside the for loop
echo "Calling GGSN throughput data bundle"
$SCRIPT --start=${START} --end=${END} --resource="GGSN_Tput"

# Finish flag for GGSN
echo "Moving GGSN PM data to ${WORKDIR}/ggsn"
mv ${WORKDIR}/*.csv ${WORKDIR}/ggsn
echo "Done executing script for GGSN"

# Script End Timing
end=$(date +%s)
runtime=$((end-start))
echo "Script done execution in ${runtime} seconds"