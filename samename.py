import jaro
location="/Users/turbo/Documents/GitHub/esi_football"

def List_Positions():
    f=open(location+"/position_penalties.csv","r")
    file=f.readlines()
    file = [i.strip("\n") for i in file]
    file = [i.split(",") for i in file]
    
    positions=dict()
    for i in file[0]:
        positions[i]=dict()
        
    for line in range(len(file)):
        pos1=file[line][0]
        for item in range(len(file[line])):
            pos2=file[0][item]
            value=file[line][item]
            
            if value !="":
                positions[pos2][pos1]=value
                positions[pos1][pos2]=value
    return positions

def List_Names():
    f=open(location+"/names.csv","r")
    file=f.readlines()
    file = [i.strip("\n") for i in file]
    file = [i.split(",") for i in file]
    
    name_dict=dict()
    for nameset in file:
        for name in nameset:
            name_dict[name]=nameset
    return name_dict

positions=List_Positions()
name_dict= List_Names()
removal=["ii","iii","iv","v","jr.","sr."]

def firstname(name1,name2):
    lowest_distance=10
    if name1 in name_dict:
        for n1 in name_dict[name1]:
            if name2 in name_dict:
                for n2 in name_dict[name2]:
                    distance=1-jaro.jaro_winkler_metric(n1,n2)
                    if distance<lowest_distance:
                        lowest_distance=distance
                return lowest_distance
            distance= 1-jaro.jaro_winkler_metric(n1,name2)
            if distance<lowest_distance:
                return lowest_distance
    return 1-jaro.jaro_winkler_metric(name1,name2)

def fixname(name):
    #suffix remove

    name=name.lower()
    name=name.replace('-','')
    name=name.replace('.','')
    name=name.replace(',','')
    name=name.replace("'",'')
    split_name=name.split(" ")
    for suffix in removal:
        if name.endswith(suffix):
            name=name[:-len(suffix)]
    if split_name[-1] in removal:
        split_name.pop(-1)

    firstname=split_name[0]
    lastname=split_name[-1]
    return firstname, lastname

def levenshtein_adjust(name1,name2):
    subtract=0
    if name1 in name2 or name2 in name1:
        subtract+=abs(len(name1)-len(name2))
        return subtract
    
    return subtract
    #firstname nicknames (do this after checking if the distance is low enough still)

def samename(name1,name2,amounts):
    first1,last1=fixname(name1)
    first2,last2=fixname(name2)
    distance1=0
    distance2=0
    
    distance1+=firstname(first1,first2)*amounts["firstname"]
    distance1+=(1-jaro.jaro_winkler_metric(last1,last2)*amounts["lastname"])
    
    distance2+=firstname(last1,first2)*amounts["firstname"]
    distance2+=(1-jaro.jaro_winkler_metric(first1,last2)*amounts["lastname"])
    
    return min(distance1,distance2)
    
def sameteam(team1,team2):
    return team1!=team2

def samepos(pos1,pos2):
    return int(positions[pos1.upper()][pos2.upper()])


def issame(player1,player2):
    
    amounts={"team":5,"position":5,"firstname":1,"lastname":1,"distance":10,"pos":1}
    
    
    distance=samename(player1["name"],player2["name"],amounts)
    distance=distance*amounts["distance"]
    distance+=amounts["pos"]*samepos(player1["position"],player2["position"])
    distance+=amounts["team"]*sameteam(player1["team"],player2["team"])
    
    return distance<2

f=open(location+"/NameList.csv","r")
file=f.readlines()
file = [i.strip("\n") for i in file]
file = [i.split(",") for i in file]

names1=[]
names2=[]
name_dict=dict()
import copy

for name in file[1:]:
    if name[1]!='':
        name_dict["name"]=name[1]
        name_dict["position"]=name[3]
        name_dict["team"]=name[2]
        names1.append(copy.deepcopy(name_dict))
    if name[4]!='':
        name_dict["name"]=name[4]
        name_dict["position"]=name[6]
        name_dict["team"]=name[5]
        names2.append(copy.deepcopy(name_dict))
maxdistance=2
for name1 in names1:
    for name2 in names2:
        distance=issame(name1,name2)
        if distance<maxdistance and distance>1:
            print(name1,name2,distance)