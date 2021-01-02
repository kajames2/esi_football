import pandas as pd
import csv

outsides= pd.read_csv('position_outsides.csv')
weights= pd.read_csv('yahoo_pos_weights.csv')
r = csv.reader(open('yahoo_projections.csv','r'))
projections=list(r)

def as_numbers(list_item):
    new_list=[]
    for item in list_item:
        new_list.append(float(item))
    return new_list

#calculate values

def sortplayers():
    players=[]
    for player in projections[1:]:
        players.append(player)
        players[-1].append(sum(as_numbers(player[4:21])))
    #sort players by value
    players.sort(key = lambda players: players[-1], reverse=True)
    return players


def teamvalue(teams,player,team_points):
    position=weights[weights['Position']==player[2]].index.values[0]

    values=[]
    team_index=-1
    
    for team in teams:
        weight=1
        for p in team:
            if p[2]==player[2]:
                weight+=1
        
        if weight<6:
            weight=weights.iat[position,weight]
        else: weight=0

        values.append(player[-1]*weight)
        #print(weight, "Weight")
    if max(values)<=0:
        return -1
    if values.count(max(values))>1:
        lowest_score=team_points[0]
        team_index=0
        for value in range(len(values)):
            if values[value]==max(values) and team_points[value]<lowest_score:
                lowest_score=team_points[value]
                team_index=value
    else:
        team_index=values.index(max(values))
    return team_index

def assignplayer(teams,team_points,players):
    for player in players:
        assign=teamvalue(teams,player,team_points)
        
        if assign>=0:
            team_points[assign]+=player[-1]
            teams[assign].append(player)
    return teams, team_points
    
def calculatepoints (team,points,players):
    global Point_Dictionary
    for player in team:
        no=players.index(player)
        value=budget*(players[no][-1]/points)
        if value>1:
            Point_Dictionary[players[no][1]]=round(value,2)
        else: 
            Point_Dictionary[players[no][1]]=1

        
budget=200
Teams=[[],[],[],[]]
Team_Points=[0,0,0,0]
Point_Dictionary={}

Players=sortplayers()
Teams, Team_Points=assignplayer(Teams,Team_Points,Players)

for t in range(len(Teams)):
    calculatepoints(Teams[t],Team_Points[t],Players)
print(Point_Dictionary)

#$/projected points = total points/total of teams

#$1 minimum per player
#can always buy an unassigned player for $1minimum
#

