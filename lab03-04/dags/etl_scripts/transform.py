import pandas as pd
import numpy as np
from google.cloud import storage
from io import StringIO
from dotenv import load_dotenv

load_dotenv() #load environment variables

# creating the global mapping for outcome types
outcomes_map = {'Rto-Adopt':1, 
                'Adoption':2, 
                'Euthanasia':3, 
                'Transfer':4,
                'Return to Owner':5, 
                'Died':6, 
                'Disposal':7,
                'Missing':8,
                'Relocate':9,
                'N/A':10,
                'Stolen':11}

# GCS stuff
storage_client = storage.Client('oceanic-hangout-406022')
bucket = storage_client.bucket('outcomes_bucket')

def transform_data(date):
    # get the data from GCS
    blob = bucket.blob(f'extracted/{date}_outcomes.csv')
    # Checking if data exists on GCS
    if blob.exists() == False:
        return

    data = blob.download_as_text()
    data = pd.read_csv(StringIO(data))

    data = prep_data(data)

    dim_animal_agg = prep_animal_dim(data)
    dim_dates = prep_date_dim(data)
    dim_outcome_types = prep_outcome_types_dim(data)
    fct_outcomes = prep_outcomes_fct(data)

    # upload to GCS
    bucket.blob(f"transformed/dim_animal_agg.csv").upload_from_string(dim_animal_agg.to_csv(index=False), 'text/csv')
    bucket.blob(f"transformed/{date}_dim_dates.csv").upload_from_string(dim_dates.to_csv(index=False), 'text/csv')
    bucket.blob(f"transformed/{date}_dim_outcome_types.csv").upload_from_string(dim_outcome_types.to_csv(index=False), 'text/csv')
    bucket.blob(f"transformed/{date}_fct_outcomes.csv").upload_from_string(fct_outcomes.to_csv(index=False), 'text/csv')        

def prep_data(data):
    # remove stars from animal names. Need regex=False so that * isn't read as regex
    data['name'] = data['name'].str.replace("*","",regex=False)

    # separate the "sex upon outcome" column into property of an animal (male or female) 
    # and property of an outcome (was the animal spayed/neutered at the shelter or not)
    data['sex'] = data['sex_upon_outcome'].replace({"Neutered Male":"M",
                                                    "Intact Male":"M", 
                                                    "Intact Female":"F", 
                                                    "Spayed Female":"F", 
                                                    "Unknown":np.nan})

    data['is_fixed'] = data['sex_upon_outcome'].replace({"Neutered Male":True,
                                                        "Intact Male":False, 
                                                        "Intact Female":False, 
                                                        "Spayed Female":True, 
                                                        "Unknown":np.nan})

    # prepare the data table for introducing the date dimension
    # we'll use condensed date as the key, e.g. '20231021'
    # time can be a separate dimension, but here we'll keep it as a field
    data['ts'] = pd.to_datetime(data.datetime)
    data['date_id'] = data.ts.dt.strftime('%Y%m%d')
    data['time'] = data.ts.dt.time

    # prepare the data table for introducing the outcome type dimension:
    # introduce keys for the outcomes
    data['outcome_type'] = data['outcome_type'].fillna('N/A')
    data['outcome_type_id'] = data['outcome_type'].replace(outcomes_map)

    return data

def prep_animal_dim(data):
    # extract columns only relevant to animal dim
    animal_dim = data[['animal_id','name','date_of_birth', 'sex', 'animal_type', 'breed', 'color']]
    
    # rename the columns to agree with the DB tables
    animal_dim.columns = ['animal_id', 'name', 'dob', 'sex', 'animal_type', 'breed', 'color']

    # Checking if data exists on GCS
    blob = bucket.blob(f'transformed/dim_animal_agg.csv')
    if blob.exists():
        #get the data from GCS
        dim_animal_agg = blob.download_as_text()
        dim_animal_agg = pd.read_csv(StringIO(dim_animal_agg))
        # append new data
        dim_animal_agg = pd.concat((dim_animal_agg, animal_dim))
    else:
        dim_animal_agg = animal_dim
    
    # drop duplicate animal records
    return dim_animal_agg.drop_duplicates()

def prep_date_dim(data):
    # use string representation as a key
    # separate out year, month, and day
    dates_dim = pd.DataFrame({
        'date_id':data.ts.dt.strftime('%Y%m%d'),
        'date':data.ts.dt.date,
        'year':data.ts.dt.year,
        'month':data.ts.dt.month,
        'day':data.ts.dt.day,
        })
    return dates_dim.drop_duplicates()

def prep_outcome_types_dim(data):
    # map outcome string values to keys
    outcome_types_dim = pd.DataFrame.from_dict(outcomes_map, orient='index').reset_index()
    
    # keep only the necessary fields
    outcome_types_dim.columns=['outcome_type', 'outcome_type_id']    
    return outcome_types_dim

def prep_outcomes_fct(data):
    # pick the necessary columns and rename
    outcomes_fct = data[["animal_id", 'date_id','time','outcome_type_id','outcome_subtype', 'is_fixed']]
    return outcomes_fct

