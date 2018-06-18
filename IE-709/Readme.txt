Hello sir,

Require Packages for run the python code 
	1. geopy (for distance calculation from lattitude and longitute)
	2. basemap (for plotting the India map)
	3. basic package like numpy,matplotlib,pulp,pandas

Zip file content one folder name as "IND_adm".this folder require to run the code
The folder contain (.shp) administrative boundaries of India state (that use by basemap package for plotting the state boundries).
Data, "Hospital.csv" consist all the Tranplant centers in India
and "Districts.csv" consist all the districts in India 


For investicating the name of selected OPO follow below:
	1."Model1.py" and "Model2.py" two code contain in the zip file (see report for detail of model1 and model2)
	2. The .csv file of all selected OPO contain in the Zip file named as "Selected_OPO"
	3. For accessing the district covered by any perticular OPO, in code we created a dictionary of OPO
	   named as "OPO_Dict",in code ("Model1.py"):
			 df_demand.iloc[OPO_Dict[key]]     
	   where key is the serial number of OPO in the file of "Selected_OPO"
	   for exmaple try ---> df_demand.iloc[OPO_Dict[1]] ; this will gives all districts covered by 
	   "Aastha Kidney and General Hospital Ganaganagar Rajasthan"
	
	4.Similar instruction can be use for "Model2.py", but model2 has 5 new OPO (as a districts)
	  so there is two dictionary ('OPO_dict') and ('NewOPO_dict')
			 df_demand.iloc[NewOPO_dict[key]]
	  key is the serial number in file "NewOPO" 
	  for example ----> df_demand.iloc[NewOPO_dict[2]]; this will gives districts covered by
	  "East Godavari, Andhra Pradesh" (new location of TC selected by Model2)


"Map1.png" show districts covarge by the existing sytem of transplant cetrers (TC)
"Map2.png" show the location of new TC (in the given existing TC system)