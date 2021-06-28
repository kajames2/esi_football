import copy
import Levenshtein
import pandas as pd

pd.set_option("display.max_columns", 40)
pd.set_option("display.max_rows", 250)
dataframes = {}
players_main = pd.DataFrame(
    columns=['Name', 'Team', 'Position']).set_index('Name')


def import_data(position):
    df_fs = pd.read_csv(
        f'https://raw.githubusercontent.com/abhinavsingh101/hello-world/master/{position}_season.csv',
        sep=',')
    df_fft = pd.read_csv(
        f'https://raw.githubusercontent.com/abhinavsingh101/hello-world/master/{position}%20Projections%202020.csv',
        sep=',')
    df_espn = pd.read_csv(
        f'https://raw.githubusercontent.com/kajames2/esi_football/master/raw_data/ESPN%20New/{position}.csv.csv',
        sep=',')
    return df_fs, df_fft, df_espn


def create_players_list():
    players_list = pd.DataFrame(columns=['Name', 'Team', 'Position'])
    return players_list


def clean_fantasy_sharks_dataframe(df_fs, players):
    for index, row in df_fs.iterrows():
        name = df_fs.loc[index, 'Player']
        intermediary_name = name.replace(',', '').split()

        # clean name
        new_name = [intermediary_name[-1], intermediary_name[0]]
        new_name = ' '.join(new_name).lower()
        for c in check_for:
            if (new_name.find(c) != -1):
                new_name = new_name.strip(c)
        df_fs['Player'] = df_fs['Player'].replace(name, new_name)
        df_fs['Site ID'] = 1

        # update players list
        if new_name not in list(players['Name'].values):
            players = players.append(
                {
                    'Name': df_fs.loc[index, 'Player'],
                    'Team': df_fs.loc[index, 'Team'],
                    'Position': df_fs.loc[index, 'Position']
                },
                ignore_index=True)

    return df_fs, players


def clean_fftoday_dataframe(df_fft, players):
    for index, row in df_fft.iterrows():
        name = df_fft.loc[index, 'Player']
        new_name = name.lower()

        # clean name
        for c in check_for:
            if (new_name.find(c) != -1):
                new_name = new_name.strip(c)

        # print(new_name)
        df_fft['Player'] = df_fft['Player'].replace(name, new_name)
        df_fft['Site ID'] = 0

        # update players list
        if new_name not in list(players['Name'].values):
            players = players.append(
                {
                    'Name': df_fft.loc[index, 'Player'],
                    'Team': df_fft.loc[index, 'Team'],
                    'Position': f'{p}'
                },
                ignore_index=True)
    return df_fft, players


def clean_espn_dataframe(df_espn, players):
    df_espn.rename(columns={'Name': 'Player'}, inplace=True)
    for index, row in df_espn.iterrows():
        name = df_espn.loc[index, 'Player']
        new_name = name.lower()

        # clean name
        for c in check_for:
            if (new_name.find(c) != -1):
                new_name = new_name.strip(c)

        # print(new_name)
        df_espn['Player'] = df_espn['Player'].replace(name, new_name)
        df_espn['Site ID'] = 2

        # update players list
        if new_name not in list(players['Name'].values):
            players = players.append(
                {
                    'Name': df_espn.loc[index, 'Player'],
                    'Team': df_espn.loc[index, 'Team'],
                    'Position': f'{p}'
                },
                ignore_index=True)

    return df_espn, players


def assign_player_id(players):
    players = players.assign(
        Player_ID=(players['Name'].astype('category').cat.codes))
    players.set_index('Name', inplace=True)
    return players


def merge_datasets(players, df_fs, df_fft, df_espn):
    df1 = pd.merge(df_fs,
                   df_fft,
                   on=['Player', 'Site ID', 'Team'],
                   how='outer',
                   suffixes=['_fs', '_fft'])
    df2 = pd.merge(df1, df_espn, on=['Player', 'Site ID', 'Team'], how='outer')
    df3 = pd.merge(df2, players, left_on='Player',
                   right_index=True).set_index(['Player_ID', 'Site ID'])
    for index, row in df3.iterrows():
        try:
            df3.loc[index, 'Team_x'] = df3.loc[index, 'Team_y']
            df3.loc[index, 'Position_x'] = df3.loc[index, 'Position_y']
        except KeyError:
            pass
    df3.rename(columns={
        "Team_x": "Team",
        "Position_x": "Position"
    },
               inplace=True)
    df3.drop(columns=['Team_y', 'Position_y'], inplace=True)

    return df3, players


close_enough_positions_dict = {
    'QB': ['QB'],
    'RB': ['RB'],
    'WR': ['WR'],
    'TE': ['TE'],
    'DT': ['DT', 'DE', 'DL', 'NT'],
    'DE': ['DE', 'DT', 'LB', 'DL', 'OLB'],
    'LB': ['LB', 'DE', 'DL', 'OLB'],
    'DL': ['DL', 'DE', 'LB', 'DT', 'NT', 'OLB'],
    'HC': ['HC'],
    'OLB': ['OLB', 'LB', 'DE', 'DL'],
    'NT': ['DT', 'NT', 'DL'],
    'S': ['S', 'DB', 'CB'],
    'CB': ['CB', 'DB', 'S'],
    'DB': ['DB', 'S', 'CB'],
    'K': ['K'],
    'P': ['P'],
    'DEF': ['DEF', 'D/ST', 'DST'],
    'D/ST': ['DEF', 'D/ST', 'DST'],
    'DST': ['DEF', 'D/ST', 'DST']
}

massive_ambiguity = {
    'S': ['S', 'DB', 'CB'],
    'CB': ['CB', 'DB', 'S'],
    'DB': ['DB', 'S', 'CB'],
}

alternative_team_abbrev_dict = {
    'ARI': ['ARI', 'ARZ'],
    'ARZ': ['ARI', 'ARZ'],
    'ATL': ['ATL'],
    'BAL': ['BAL', 'BLT'],
    'BLT': ['BAL', 'BLT'],
    'BUF': ['BUF'],
    'CAR': ['CAR'],
    'CHI': ['CHI'],
    'CIN': ['CIN'],
    'CLE': ['CLE', 'CLV'],
    'CLV': ['CLE', 'CLV'],
    'DAL': ['DAL'],
    'DEN': ['DEN'],
    'DET': ['DET'],
    'FA': ['FA', 'FA*', 'RET', ''],
    'FA*': ['FA', 'FA*', 'RET', ''],
    'GBP': ['GBP', 'GB'],
    'GB': ['GBP', 'GB'],
    'HOU': ['HOU', 'HST'],
    'HST': ['HOU', 'HST'],
    'IND': ['IND'],
    'JAC': ['JAC', 'JAX'],
    'JAX': ['JAC', 'JAX'],
    'KCC': ['KCC', 'KC'],
    'KC': ['KCC', 'KC'],
    'LAC': ['LAC', 'SDC', 'SD'],
    'SDC': ['LAC', 'SDC', 'SD'],
    'SD': ['LAC', 'SDC', 'SD'],
    'LAR': ['LAR', 'LA', 'STL'],
    'LA': ['LAR', 'LA', 'STL'],
    'STL': ['LAR', 'LA', 'STL'],
    'MIA': ['MIA'],
    'MIN': ['MIN'],
    'NEP': ['NEP', 'NE'],
    'NE': ['NEP', 'NE'],
    'NOS': ['NOS', 'NO', 'NOR'],
    'NO': ['NOS', 'NO', 'NOR'],
    'NOR': ['NOS', 'NO', 'NOR'],
    'NYG': ['NYG'],
    'NYJ': ['NYJ'],
    'OAK': ['LVR', 'OAK', 'LV'],
    'LVR': ['LVR', 'OAK', 'LV'],
    'LV': ['LVR', 'OAK', 'LV'],
    'PHI': ['PHI'],
    'PIT': ['PIT'],
    'RET': ['FA', 'FA*', 'RET', ''],
    'SEA': ['SEA'],
    'SFO': ['SFO', 'SF'],
    'SF': ['SFO', 'SF'],
    'TBB': ['TBB', 'TB'],
    'TB': ['TBB', 'TB'],
    'TEN': ['TEN'],
    'WAS': ['WAS', 'WSH'],
    'WSH': ['WAS', 'WSH'],
    '': ['FA', 'FA*', 'RET', '']
}
# 'DB': ['S', 'CB']
# 'DL': ['DT', 'DE', 'OLB']
# 'DL': ['DL', 'DE', 'DT', 'OLB']

# ambiguous_positions_espn = ['CB', 'DST',  'HC', 'P']
# ambiguous_positions_fs = [ 'P', 'C', 'CB',  ]
positions_fft = ['QB', 'RB', 'WR', 'TE', 'K', 'LB', 'DE', 'DL', 'DB']
positiont_fs = ['QB', 'RB', 'WR', 'TE', 'K', 'LB', 'DE', 'DT', 'S']
positions_espn = ['QB', 'RB', 'WR', 'TE', 'K', 'LB', 'DE', 'DT', 'S']

pos_name = list(zip())
# pos_name = ['QB', 'RB','WR','TE','K','LB']
check_for = ['iii', 'jr.', 'sr.']


# list(dataframes['QB'].columns)
def convert(string):
    list1 = []
    list1[:0] = string
    return list1


# more details for each position need to be added
def position_wise_cleaning(position, df):
    if position == 'QB':
        for index, row in df.iterrows():
            try:
                df.at[(index[0], 0), 'Att_fs'] = df.at[(index[0], 0),
                                                       'Att_fft']
                df.at[(index[0], 0), 'Comp_fs'] = df.at[(index[0], 0),
                                                        'Comp_fft']
                df.at[(index[0], 0), 'Int'] = df.at[(index[0], 0), 'INT']
                # 'Rush Yds_y', 'Int_y', 'Pass Yds_y','Rush Yds_x','Rush TDs', 'Comp_fft', 'Att_fft',
            except KeyError:
                pass
        df = df.rename(columns={
            'Att_fs': 'PassAtt',
            'Comp_fs': 'PassComp'
        }).drop(columns=['Comp_fft', 'Att_fft'])
    return df


def player_distance(player1, player2):
    (name1, team1, pos1) = player1
    (name2, team2, pos2) = player2
    distance = (2 * (not same_position(pos1, pos2)) + 2 *
                (not same_team(team1, team2)))
    if 'DEF' not in close_enough_positions_dict[pos2.upper()]:
        distance += name_distance(name1, name2)
    return distance


def name_distance(name1, name2):
    return Levenshtein.distance(name1, name2)


def same_position(pos1, pos2):
    return pos2.upper() in close_enough_positions_dict[pos1.upper()]


def same_team(team1, team2):
    return team2.upper() in alternative_team_abbrev_dict[team1.upper()]


def main():
    dataframes_fs = {}
    dataframes_fft = {}
    dataframes_espn = {}
    for p in pos_name:
        df_fs, df_fft, df_espn = import_data(p)
        players = create_players_list()
        df_fs, players = clean_fantasy_sharks_dataframe(df_fs, players)
        df_fft, players = clean_fftoday_dataframe(df_fft, players)
        df_espn, players = clean_espn_dataframe(df_espn, players)
        dataframes_fs[p] = df_fs
        dataframes_fft[p] = df_fft
        dataframes_espn[p] = df_espn
        players_main = players_main.append(players)

    players_main = assign_player_id(players_main)
    for p in pos_name:
        df_fs = dataframes_fs[p]
        df_fft = dataframes_fft[p]
        df_espn = dataframes_espn[p]
        df, players_main = merge_datasets(players_main, df_fs, df_fft, df_espn)
        dataframes[f"{p}"] = df

    all_columns = []
    for p in pos_name:
        columns_list = list(dataframes[p].columns)
        for k in range(len(columns_list)):
            all_columns.append(columns_list[k])

    all_columns
    df_cols = pd.DataFrame(all_columns)
    df_cols.to_csv('column_names.csv', index=False)

    players_main.sample(5)
    players_with_no_pairs = []
    for pos in pos_name:
        players_for_this_pos = players_main[players_main.Position == f'{pos}']
        for player_id in players_for_this_pos['Player_ID'].values:
            for i in [0, 1]:
                if dataframes[f'{pos}'].index.isin([(player_id, i)]).any():
                    pass
                else:
                    players_with_no_pairs.append(
                        players_for_this_pos[players_for_this_pos['Player_ID']
                                             == player_id].index.values[0])

    players_data = copy.deepcopy(players_main)
    N = 9
    threshold = 4
    levenshtein_d = []
    for index, row in players_main.iterrows():
        name1 = index
        team1 = players_main.loc[index, 'Team']
        pos1 = players_main.loc[index, 'Position']
        p1 = (name1, team1, pos1)
        players_data = copy.deepcopy(players_main)
        players_data.drop(name1)
        player_distances = {}
        for index2, row2 in players_data.iterrows():
            name2 = index2
            team2 = players_data.loc[index, 'Team']
            pos2 = players_data.loc[index, 'Position']
            p2 = (name2, team2, pos2)
            distance = player_distance(p1, p2)
            player_distances[name2] = distance
        dist_dict = {
            k: v
            for k, v in sorted(player_distances.items(),
                               key=lambda item: item[1])[0:N]
        }
        dist_dict2 = {}
        for k, v in dist_dict.items():
            if v <= threshold:
                dist_dict2[k] = v
        levenshtein_d.append(dist_dict2)
