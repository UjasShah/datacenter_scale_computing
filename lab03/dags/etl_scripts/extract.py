from sodapy import Socrata
import pandas as pd
import os
from dotenv import load_dotenv
from google.cloud import storage

load_dotenv() #load environment variables

storage_client = storage.Client('oceanic-hangout-406022')
bucket = storage_client.bucket('outcomes_bucket')
folder_name = 'extracted/'

def extract_data(date):
    client = Socrata("data.austintexas.gov",
                     os.getenv('APP_TOKEN'),
                     username= os.getenv('USERNAME'),
                     password = os.getenv('PASSWORD'))
    
    # check if there is an extracted folder in the bucket
    blobs = bucket.list_blobs(prefix=folder_name)
    if len(list(blobs)) == 0:
        #extract all data till the date
        results = client.get("9t4d-g238", where = f"datetime <= '{date}'", limit = 200000)
    else:
        #extract data for the date
        results = client.get("9t4d-g238", where = f"date_trunc_ymd(datetime) = '{date}'")

    if len(results) != 0:
        results_df = pd.DataFrame.from_records(results)
        # upload to GCS
        blob = bucket.blob(f"extracted/{date}_outcomes.csv")
        blob.upload_from_string(results_df.to_csv(index=False), 'text/csv')