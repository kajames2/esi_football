#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on Thu Sep 10 19:33:26 2020
MUST BE EDITED TO DIFFERNTIATE ATTEMPTS YARDS AND TDS BETWEEN OFFENSIVE PLAYERS
@author: Jacob Cohn
'''

import requests
from pathlib import Path
from bs4 import BeautifulSoup
from bs4 import NavigableString
import csv



def main():
    positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DEF', 'DL', 'LB', 'DB']
    for pos in positions:
        print(f'Downloading {pos} projections')
        pg_no = 0
        are_more_pages = True
        dataset = []
        while are_more_pages:
            soup = download_page(pos, pg_no)
            if pg_no == 0:
                columns = parse_columns(soup)
            dataset += parse_players(soup, len(columns))
            are_more_pages = is_next_page(soup)
            pg_no += 1
        export_position_projections(columns, dataset, pos)

pos_ids = {'QB': 10,
           'RB': 20,
           'WR': 30,
           'TE': 40,
           'K': 80,
           'DEF': 99,
           'DL': 50,
           'LB' : 60,
           'DB': 70}
def download_page(pos, pg_no):
    website = f'https://fftoday.com/rankings/playerproj.php?PosID={pos_ids[pos]}&LeagueID='
    page_var = f'Season=2020&order_by=FFPts&sort_order=DESC&cur_page={pg_no}'
    page = requests.get(website + '&' + page_var)
    return BeautifulSoup(page.content, 'html.parser')

def parse_columns(soup):
    column_header = soup.select('.tableclmhdr')[0]
    columns = [b.get_text() for b in column_header.find_all('b')]
    return columns

def parse_players(soup, n_columns):
    entries = soup.find_all('table')[7].find_all(class_='smallbody')
    entries = [entry.get_text().strip() for entry in entries]
    entries = list(partition(entries, n_columns))
    return entries

def partition(l, n):
	for i in range(0, len(l), n):
		yield l[i : i+n]

def is_next_page(soup):
    footer = soup.find_all('div')[-4].get_text()
    return 'Next Page' in footer

def export_position_projections(columns, dataset, pos):
    # Get rid of Chg column
    columns = columns[1:]
    dataset = [row[1:] for row in dataset]
    folder = '.'
    Path(folder).mkdir(parents=True, exist_ok=True)
    with open(f'{folder}/{pos}.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(columns)
        writer.writerows(dataset)


if __name__ == '__main__':
    main()
