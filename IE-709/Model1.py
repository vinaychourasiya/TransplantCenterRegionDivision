from pulp import *
from mpl_toolkits.basemap import Basemap
import os
import pandas as pd
import numpy as np
import geopy.distance as gd
import matplotlib.pyplot as plt



#Read CSV file
df_TC=pd.read_csv('Hospital.csv')
df_demand=pd.read_csv('Districts.csv',encoding='ISO-8859-1')

def DataFile():
    """
    this function takes input .csv file of hospital and 
    give output is the distances between base on the lat
    long of the location 
    """
    LatTC = df_TC['Lat'].values
    LongTC=df_TC['log'].values
    LatDemand=df_demand['Lat'].values
    LongDemand=df_demand['Long'].values
    # making the matric and transposing it so (lat,long) form
    TC=np.transpose(np.array((LatTC,LongTC)))
    Demand=np.transpose(np.array((LatDemand,LongDemand)))
    Pop=df_demand['Population']
    
    #distance matrix DisMat
    DisMat=[]
    #print(df_TC.head())
    for loc1 in TC:
        D=[]
        for loc2 in Demand:
            d=gd.vincenty(loc1, loc2).km
            D.append(d)
        DisMat.append(D)
    DisMat=np.array(DisMat)
    DistanceDf=pd.DataFrame(DisMat)
    #W=df_TC['pop_den'].values
    # avg speed of travel kmph of organ transport vehicle
    S = 80
    #Available time to transport the organ  in hours
    TimeKindney = 18
    TimeLiver= 6
    #max distance can be cover for  kidney
    DisKidney = TimeKindney*S
    #max distance can be cover for  liver
    DisLever=TimeLiver*S
    #binary matrix (0,1) for allowable feasible location 
    #that come under the range of available time
    DisKidney_binary = (DistanceDf <= DisKidney)*1
    
    DisLever_binary=(DistanceDf<= DisLever)*1
    #DisKidney_binary.to_csv('AvKidney.txt', sep='\t')
    #DisLever_binary.to_csv('Avlever.txt', sep='\t')
    Binary_Kidney=DisKidney_binary.values
    Binary_Liver=DisLever_binary.values
    #for return purpose we create list of kidney and liver
    return (DisMat,Pop,Binary_Kidney,Binary_Liver)

D,W,Bin_Kidney,Bin_liver=DataFile()
#D=distance matricx from each TC to Demand point
#===========================PULP==============================
#define problem
prob = pulp.LpProblem('Optimal Transplantation location', pulp.LpMinimize)
s=D.shape
#TC_loc transplantation loaction no.    
TC_loc = range(s[0])
Demand_loc=range(s[1])
# Define variable   
x = LpVariable.dicts('x',TC_loc ,upBound=1, lowBound=0,cat=pulp.LpInteger)
y = LpVariable.dicts('y',[(i,j) for i in TC_loc for j in Demand_loc],upBound=1, lowBound=0,cat=pulp.LpInteger)
    
# Objective Function 
prob += lpSum(W[j]*y[(i,j)]*D[i][j] for i in TC_loc for j in Demand_loc)
    
# Constraints 
for j in Demand_loc:
    prob += lpSum( y[(i,j)] for i in TC_loc) == 1

for i in TC_loc:
     for j in Demand_loc:
         prob += y[(i,j)] - x[i] <=0



for i in TC_loc:
     for j in Demand_loc:
         prob += y[(i,j)] <= Bin_liver[i][j]

   
prob.solve()
    
#Status of Given Programme
    
#print ("Status:", LpStatus[prob.status])
print ("Objective value = ", value(prob.objective))
OPO=[]         
for candLoc in TC_loc:
    if x[candLoc].varValue==1:
        OPO.append(candLoc)
print("Locations selected as OPO",OPO)
B=[]
a=[]
for o in OPO:
    for i in Demand_loc:
        if y[o,i].varValue==1:
            a.append(i)
    B.append(a)
    a=[]
#================================Map Plotting====================
LatTC = df_TC['Lat'].values
LongTC=df_TC['log'].values
LatDemand=df_demand['Lat'].values
LongDemand=df_demand['Long'].values

AllNode=list(zip(OPO,B))
All_lat=[]
All_long=[]
for R in AllNode:
    #TClat=LatTC[R[0]]
    Dlat=LatDemand[R[1]]
    #TClong=LongTC[R[0]]
    Dlong=LongDemand[R[1]]
    All_lat.append(Dlat)
    All_long.append(Dlong)
TClat = LatTC[OPO]
TClong=LongTC[OPO]
DFOPO = df_TC.iloc[OPO]
LatOPO=DFOPO['Lat'].values
LongOPO=DFOPO['log'].values
#sns.set(rc={"figure.figsize": (6, 6)})
#np.random.seed(sum(map(ord, "palettes")))
plt.figure(dpi=150)
m= Basemap(projection='mill',
           llcrnrlat=3,
           llcrnrlon=66,
           urcrnrlat=37,
           urcrnrlon=100,
           resolution='l')
m.drawcoastlines()
m.readshapefile(os.path.join('IND_adm', 'IND_adm1'),'IN')
m.fillcontinents()

m.etopo()

shape= list(["1",'4','<','o','^','x','+','d','H','p','s'])

color=['r','b','g','c','m','k','y']
for i in range(len(OPO)):
    z=np.random.choice(shape)
    c=np.random.choice(color)
    x,y=m(All_long[i],All_lat[i])
    plt.plot(x,y,c+z)
   

OPO_Dict = dict(AllNode)

plt.title('Map shows Districts allocation to OPO')
plt.savefig('MAP1.png',bbox_inches='tight')
plt.close()
print("Map of existing OPO and new OPO location save as 'MAP1.png' ")  
#Objective value =  138556554318.07944












