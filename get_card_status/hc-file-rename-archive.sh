#!/bin/sh

shopt -s nullglob

datenow=$(date +%s)

for file in tmp/*; do
    mv $file ${file}-${datenow}.log
done

cd tmp ; tar -czvf ../output/staros-hc-${datenow}.tar.gz .
