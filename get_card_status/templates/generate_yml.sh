#!/bin/bash

export dateepoch=$(date +%s)

rm -f health_check.yml temp.yml

( echo "cat <<EOF >../tasks/main.yml";
  cat health_check_template.yml;
) >temp.yml

. temp.yml

rm -f temp.yml
