import pandas as pd
import numpy as np

# function that return dictionary of top 10 airport departure datasets
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

    # only keep entries of airports in list of 10 busiest airports
    airports_top10 = ["ATL", "DFW", "DEN", "LAX", "ORD", "JFK", "MCO", "LAS", "CLT", "MIA"]

    # use boolean mask to select all rows with airports_top10 
    dep_data_top10 = dep_data[dep_data["ORIGIN"].isin(airports_top10)]
    dep_data_top10.reset_index(drop=True)

    # assign each airport to a seperate dataset. datasets are stores in dict. (datasets[{airport code}])
    datasets = {}
    for n in airports_top10:
        datasets[n] = dep_data_top10.loc[dep_data_top10["ORIGIN"]==n].reset_index(drop=True)
    
    return datasets

#datasets = departure_datasets()
#print(datasets["ATL"])