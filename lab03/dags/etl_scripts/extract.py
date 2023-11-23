from sodapy import Socrata
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv() #load environment variables

AIRFLOW_HOME = os.environ.get('AIRFLOW_HOME', 'opt/airflow')
EXTRACT_DIR = os.path.join(AIRFLOW_HOME, 'data', 'extracted')

# Create the directory if it doesn't exist
os.makedirs(EXTRACT_DIR, exist_ok=True)

# assert os.getenv('APP_TOKEN') is not None, "You must set APP_TOKEN in your environment variables"

def extract_data(date):
    client = Socrata("data.austintexas.gov",
                     os.getenv('APP_TOKEN'),
                     username= os.getenv('USERNAME'),
                     password = os.getenv('PASSWORD'))
    
    # check if EXTRACT_DIR is empty
    if os.listdir(EXTRACT_DIR) == []:
        #extract all data till the date
        results = client.get("9t4d-g238", where = f"datetime <= '{date}'", limit = 2000) #CHANGE THIS NUMBER
    else:
        #extract data for the date
        results = client.get("9t4d-g238", where = f"date_trunc_ymd(datetime) = '{date}'")

    results_df = pd.DataFrame.from_records(results)
    results_df.to_csv(os.path.join(EXTRACT_DIR, f"{date}_outcomes.csv"))