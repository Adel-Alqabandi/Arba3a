######################################################################
# function that returns pickle dictionary of top 10 airport departure datasets

# to select dataset of an airport, use the airport code as the key in the dict datasets
# e.g. datasets["LAX"]
#####################################################################

import pandas as pd
import pickle

def departure_datasets():
    # read .csv files and append into one big dataset
    df_appended = []
    for m in [23,24]:
        for n in range(1, 10):  
            if (m==24) and (n>10):
                pass
            else:
                df = pd.read_csv(f"Datasets/Departures Dataset/20{m}/Departures {n}-{m}.csv")
                df_appended.append(df)

    dep_data = pd.concat(df_appended, ignore_index=True)

    # replacing the record time from FL_DATE with the planned departure date
    # convert FL_DATE column into datetime object 
    dep_data["FL_DATE"] = pd.to_datetime(dep_data["FL_DATE"], format="%m/%d/%Y %I:%M:%S %p")

    # add colon to seperate hours and minutes
    dep_data["CRS_DEP_TIME"] = dep_data["CRS_DEP_TIME"].astype(str).str.zfill(4)  #"530" becomes "0530"
    dep_data["CRS_DEP_TIME"] = dep_data["CRS_DEP_TIME"].str[:2] + ":" + dep_data["CRS_DEP_TIME"].str[2:]

    # some records incorrectly interpret 00:00 as 24:00
    dep_data["CRS_DEP_TIME"] = dep_data["CRS_DEP_TIME"].replace("24:00", "00:00")

    # convert CRS_DEP_TIME into datetime object
    dep_data["CRS_DEP_TIME"] = pd.to_datetime(dep_data["CRS_DEP_TIME"], format="%H:%M")

    # taking only the date from FL_DATE and combining with time from CRS_DEP_TIME
    dep_data["FL_DATETIME"] = (dep_data["FL_DATE"].dt.strftime("%d/%m/%Y") + " " + dep_data["CRS_DEP_TIME"].dt.strftime("%H:%M"))

    # removing irrelevant columns
    dep_data = dep_data.drop(columns=["FL_DATE", "CRS_DEP_TIME"])

    # only keep entries of airports in list of 10 busiest airports
    airports_top10 = ["ATL", "DFW", "DEN", "LAX", "ORD", "JFK", "MCO", "LAS", "CLT", "MIA"]

    # use boolean mask to select all rows with airports_top10 
    dep_data_top10 = dep_data[dep_data["ORIGIN"].isin(airports_top10)]
    dep_data_top10.reset_index(drop=True)

    # assign each airport to a seperate dataset. datasets are stores in dict. (datasets[{airport code}])
    datasets = {}
    for n in airports_top10:
        datasets[n] = dep_data_top10.loc[dep_data_top10["ORIGIN"]==n].reset_index(drop=True)
    
    # writing datasets to pickle file
    with open("flight_datasets.pkl", "wb") as file:
        pickle.dump(datasets, file)

# running the function
#departure_datasets()