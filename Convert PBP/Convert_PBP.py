import pandas as pd

plays= pd.read_csv('PBP.csv')

def getSeason(dfObj, value):
    ''' Get i positions of value in dataframe i.e. dfObj.'''
    list_rows = list()
    # Get bool dataframe with True at positions where the given value exists
    result = dfObj.isin([value])
    # Get list of columns that contains the value
    seriesObj = result.any()
    columnNames = list(seriesObj[seriesObj == True].index)
    print(columnNames)
    # Iterate over list of columns and fetch the rows ies where value exists
    for col in columnNames:
        rows = list(result[col][result[col] == True].index)
        for row in rows:
            list_rows.append((row))
    # Return a list of tuples iicating the positions of value in the dataframe
    return list_rows

def gameIndices(dfObj, game):
    i=len(dfObj)/10
    index=0
    gameFound=False
    gameStart=False
    gameEnd=False
    while not gameStart:
        while not gameFound:
            index+=int(i) #i must be an integer
            
            if index >= len(dfObj): #when i exceeds df length, cut iteration by 2
                i=i/2
                index=0 #return i to 0
                if i<=0:
                    return 0
            elif dfObj['gid'][index]==game:
                gameFound=True
        index-=1
        if index<0:
            index+=1
            gameStart=True
        if dfObj['gid'][index]!=game:
            index+=1
            gameStart=True
    gameStart=index
    while not gameEnd:
        index+=1
        if index>len(dfObj):
            index-=1
            gameEnd=True         
        if dfObj['gid'][index]!=game:
            index-=1
            gameEnd=True
    gameEnd=index
    
    return dfObj[gameStart:gameEnd]
   
def getPlayers(dfObj,game): 
    columns=['bc','rtck1','rtck2']
    listplayers=dict()
    for col in columns:
        listplayers[col]=[]
    dfObj = gameIndices(dfObj,game)
    for row in range(len(dfObj)):
        for col in columns:
            if not pd.isna(dfObj[col][row]):
                listplayers[col].append(dfObj[col][row])
    return listplayers

def getGame (dfObj, value, game):
    dfObj = gameIndices(dfObj,game)

    list_rows=list()
    result = dfObj.isin([value])
    # Get list of columns that contains the value
    seriesObj = result.any()
    columnNames = list(seriesObj[seriesObj == True].index)
        
    for col in columnNames:
        rows = list(result[col][result[col] == True].index)
        for row in rows:
            list_rows.append((row))
    # Return a list of tuples iicating the positions of value in the dataframe
    return list_rows

def getYards(dfObj,rows):
    count= []
    for row in rows:
        if not pd.isna(dfObj['yds'][row]):
            count.append(dfObj['yds'][row])
    return count

def getTackles (dfObj, rows, player):
    count=[]
    for row in rows:
        if not pd.isna(dfObj['rtck1'][row]):
            count.append(1)
            if not pd.isna(dfObj['rtck2'][row]):
                count[-1]=.5
    return count



list_rows=getGame(plays,'CG-0400',1)
print(sum(getYards(plays,list_rows)))