#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 13:29:58 2020

@author: jacob
"""
from pathlib import Path
import requests

# headers is needed so fantasysharks knows what browser we claim to be using.
headers = {'User-Agent': 'Chrome/39.0.2171.95'}

pos_inds = {'QB': 1,
            'RB': 2,
            'WR': 4,
            'TE': 5,
            'K': 7,
            'LB': 9,
            'DE': 19,
            'DT': 18,
            'CB': 16,
            'S': 17,
            'P': 15,
            'C': 29}

def download_weekly_sharks_data(position, week):
    segment = 691 + week
    pos_ind = pos_inds[position]
    return download_sharks_data(segment, pos_ind)


def download_season_sharks_data(position):
    segment = 682
    pos_ind = pos_inds[position]
    return download_sharks_data(segment, pos_ind)


def download_sharks_data(segment, pos_ind):
    url = ('https://www.fantasysharks.com/apps/bert/forecasts/projections.php?csv=1&Sort=&Segment='
           + str(segment) + '&Position=' + str(pos_ind) + '&scoring=2&League=&uid=4&uid2=&printable=')
    r = requests.get(url, headers=headers)
    return r.content


def scrape_weekly_projection(week, position, base_dir):
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    data = download_weekly_sharks_data(position, week)
    open(f'{base_dir}/{position}_week_{week}.csv', 'wb').write(data)


def scrape_season_projection(position, base_dir):
    Path(base_dir).mkdir(parents=True, exist_ok=True)
    data = download_season_sharks_data(position)
    open(f'{base_dir}/{position}_season.csv', 'wb').write(data)


def main():
    positions = ['QB', 'RB', 'WR', 'TE', 'K', 'LB', 'DE', 'DT', 'CB', 'S', 'P', 'C']
    base_dir = '.'
    n_weeks = 17
    for position in positions:
        print(f'Downloading {position} projections')
        for week in range(1, n_weeks + 1):
            scrape_weekly_projection(week, position, base_dir)
        scrape_season_projection(position, base_dir)


if __name__ == "__main__":
    main()
