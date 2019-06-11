#!/usr/bin/env python3

# Import modules
import glob
import re
import os
import csv

# Nodename getter
def get_node_name(card_log):
    nodename = card_log.split('-')[-3].split('/')[-1]
    return nodename

# CF Cards getter
def get_cf_cards(card_log):
    f = open(card_log, "r")
    fl = f.readlines()
    cf_cards_raw = [line for line in fl if "Control Function Virtual Card" in line]
    cf_cards_fixed_num = []
    for i in range(len(cf_cards_raw)):
        cf_cards_fixed_num.append(int(re.sub(r'\W+',' ', cf_cards_raw[i]).split()[0]))
    f.close()
    return cf_cards_fixed_num

# SF Standby Cards getter
def get_sf_standby(card_log):
    f = open(card_log, "r")
    fl = f.readlines()
    sf_standby_cards = [line for line in fl if "Service Function Virtual Card" in line and "Standby" in line]
    sf_standby_cards_num = []
    for i in range(len(sf_standby_cards)):
        sf_standby_cards_num.append(int(re.sub(r'\W+',' ', sf_standby_cards[i]).split()[0]))
    f.close()
    return sf_standby_cards_num

# Demux cards getter
def get_demux_card(card_log):
    f = open(card_log, "r")
    fl = f.readlines()
    demux_cards = [line for line in fl if "Demux" in line]
    demux_cards_num = []
    for i in range(len(demux_cards)):
        demux_cards_num.append(int(re.sub(r'\W+',' ', demux_cards[i]).split()[0]))
    f.close()
    return demux_cards_num

# Print comma-separated list into string with semicolon delimiter. Keep the brackets
def stringify_list_with_semicolon(list_card):
    return re.sub(", ", ";", str(list_card))

# Make a list from collection of strings above
def make_card_list(nodename, cf_cards, sf_standby_cards, demux_cards):
    card_list = []
    card_list.append(nodename)
    card_list.append(stringify_list_with_semicolon(cf_cards))
    card_list.append(stringify_list_with_semicolon(sf_standby_cards))
    card_list.append(stringify_list_with_semicolon(demux_cards))
    return card_list

# Loop through logs file and make a list of node's card roles
def loop_through_files_make_list():
    card_list = []
    path = "/Users/Gandhi/Documents/GitHub/staros-ansible-playbook/get_card_status/tmp"
    files = [f for f in glob.glob(path + "/*.log", recursive=True)]
    #for filename in os.listdir('/Users/Gandhi/Documents/GitHub/staros-ansible-playbook/get_card_status/tmp/'):
    for filename in files:
        if filename.endswith(".log"):
            nodename = get_node_name(filename)
            cf_cards = get_cf_cards(filename)
            sf_standby_cards = get_sf_standby(filename)
            demux_cards = get_demux_card(filename)
            card_list_member = make_card_list(nodename, cf_cards, sf_standby_cards, demux_cards)
            card_list.append(card_list_member)
    return card_list

# Make a csv file from card list above
def make_csv(card_list):
    with open('/Users/Gandhi/Documents/GitHub/staros-ansible-playbook/get_card_status/output/card.csv', 'w') as csvfile:
        wr = csv.writer(csvfile)
        wr.writerow(['node', 'cf', 'sf_standby', 'demux'])
        wr.writerows(card_list)

# Begin main function
def main():
	card_list = loop_through_files_make_list()
	make_csv(card_list)

if __name__ == "__main__":
	main()


