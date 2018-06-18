from pulp import *
from mpl_toolkits.basemap import Basemap
import os
import pandas as pd
import numpy as np
import geopy.distance as gd
import matplotlib.pyplot as plt
#import seaborn as sns

print("program is running...")
#Read CSV file
df_TC=pd.read_csv('Hospital.csv')
df_demand=pd.read_csv('Districts.csv',encoding='ISO-8859-1')

def DataFile():
    """
    this function takes input .csv file of hospital and 
    give output is the distances between base on the lat
    long of the location and required data.
    """
    LatTC = df_TC['Lat'].values
    LongTC=df_TC['log'].values
    LatDemand=df_demand['Lat'].values
    LongDemand=df_demand['Long'].values
    # making the matric and transposing for making array like --> (lat,long) form
    TC=np.transpose(np.array((LatTC,LongTC)))
    Demand=np.transpose(np.array((LatDemand,LongDemand)))
    PopDensity=df_demand['Population']
    
    #distance matrix DisMat
    DisMat_F=[]
    #print(df_TC.head())
    for loc1 in Demand:
        D=[]
        for loc2 in TC:
            d=gd.vincenty(loc1, loc2).km
            D.append(d)
        DisMat_F.append(D)
    DisMat_F=np.array(DisMat_F)
    DistanceDf1=pd.DataFrame(DisMat_F)
    #for distric to distric distance
    DisMat_D=[]
    for loc1 in Demand:
        D=[]
        for loc2 in Demand:
            d=gd.vincenty(loc1, loc2).km
            D.append(d)
        DisMat_D.append(D)
    DisMat_D=np.array(DisMat_D)
    DistanceDf2=pd.DataFrame(DisMat_D)
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
    #DisKidney_binaryF = (DistanceDf1 <= DisKidney)*1
    #DisKidney_binaryD = (DistanceDf2 <= DisKidney)*1
    
    DisLever_binaryF=(DistanceDf1<= DisLever)*1
    DisLever_binaryD=(DistanceDf2<= DisLever)*1
    #DisKidney_binary.to_csv('AvKidney.txt', sep='\t')
    #DisLever_binary.to_csv('Avlever.txt', sep='\t')
    Binary_LiverF=DisLever_binaryF.values
    Binary_LiverD=DisLever_binaryD.values
    #for return purpose we create list of kidney and liver
    return (DisMat_F,DisMat_D,PopDensity,Binary_LiverF,Binary_LiverD)

D1,D2,W,Bin_F,Bin_D =DataFile()
#D=distance matricx from each TC to Demand point
#===========================PULP==============================
#define problem

p=5  # new facility No. 
prob = pulp.LpProblem('ADD_FACILITY_loc', pulp.LpMinimize)
s=D1.shape
#TC_loc transplantation loaction no.    
Demand_loc = range(s[0])
TC_loc=range(s[1])
print("I am in PULP")
# Define variable   
x = LpVariable.dicts('x',TC_loc ,upBound=1, lowBound=0,cat=pulp.LpInteger)
A = LpVariable.dicts('A',Demand_loc ,upBound=1, lowBound=0,cat=pulp.LpInteger)
y = LpVariable.dicts('y',[(i,j) for i in Demand_loc  for j in TC_loc ],upBound=1, lowBound=0,cat=pulp.LpInteger)
z = LpVariable.dicts('z',[(i,k) for i in Demand_loc for k in Demand_loc],upBound=1, lowBound=0,cat=pulp.LpInteger)
# Objective Function 
prob += lpSum([W[i]*y[(i,j)]*D1[i][j] for i in Demand_loc for j in TC_loc] + 
               [W[i]*z[(i,k)]*D2[i][k] for i in Demand_loc  for k in Demand_loc])
# Constraints 
for i in Demand_loc:
    prob += lpSum( [y[(i,j)] for j in TC_loc]+ [z[(i,k)] for k in Demand_loc]) == 1

for j in TC_loc:
     for i in Demand_loc:
         prob += y[(i,j)] - x[j] <=0

for k in Demand_loc:
     for i in Demand_loc:
         prob += z[(i,k)] - A[k] <=0

prob += lpSum(A[k] for k in Demand_loc)==p

for j in TC_loc:
     for i in Demand_loc:
         prob += y[(i,j)] <= Bin_F[i][j]

for k in Demand_loc:
     for i in Demand_loc:
         prob += z[(i,k)] <= Bin_D[i][k]

print("Now solve the problem ,wait....")
prob.solve()
    
#Status of Given Programme
    
print ("Status:", LpStatus[prob.status])
print ("Objective value = ", value(prob.objective))
OPO=[]
OPO_new=[]         
for candLoc in TC_loc:
    if x[candLoc].varValue==1:
        OPO.append(candLoc)
for Loc in Demand_loc:
    if A[Loc].varValue==1:
        OPO_new.append(Loc)


B1=[]
for o in OPO:
    a=[]
    for i in Demand_loc:
        if y[i,o].varValue==1:
            a.append(i)
    B1.append(a)
B2=[]
for o in OPO_new:
    a=[]
    for i in Demand_loc:
        if z[i,o].varValue==1:
            a.append(i)
    B2.append(a)

#================================Map Plotting====================
LatTC = df_TC['Lat'].values
LongTC=df_TC['log'].values
LatDemand=df_demand['Lat'].values
LongDemand=df_demand['Long'].values

AllNode1=list(zip(OPO,B1))
AllNode2=list(zip(OPO_new,B2))

OPO_dict = dict(AllNode1) 
NewOPO_dict =dict(AllNode2)


All_lat1=[]
All_long1=[]

All_lat2=[]
All_long2=[]

for R in AllNode1:
    Dlat=LatDemand[R[1]]
    Dlong=LongDemand[R[1]]
    All_lat1.append(Dlat)
    All_long1.append(Dlong)

for R in AllNode2:
    Dlat=LatDemand[R[1]]
    Dlong=LongDemand[R[1]]
    All_lat2.append(Dlat)
    All_long2.append(Dlong)

LatOPO = df_TC['Lat'].values
LongOPO=df_TC['log'].values
NewDf = df_demand.iloc[OPO_new]
LatN =NewDf['Lat'].values
LongN= NewDf['Long'].values

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


x1,y1=m(LongOPO,LatOPO)
x2,y2=m(LongN,LatN)
plt.plot(x1,y1,'g^',label='OPOs')
plt.plot(x2,y2,'bo',label='New')
plt.title('Hospitals which selected as OPO')
plt.legend(loc='upper right', numpoints=1)
plt.savefig('MAP2.png',bbox_inches='tight')
plt.close()
print("Map of existing OPO and new OPO location save as 'MAP2.png' ")
   
#Objective value =  114305208409.3736










