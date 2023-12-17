from google.cloud import bigquery
from google.cloud import storage
from google.cloud.exceptions import NotFound
from dotenv import load_dotenv

load_dotenv() #load environment variables

# GCS stuff
storage_client = storage.Client('oceanic-hangout-406022')
bucket = storage_client.bucket('outcomes_bucket')

client = bigquery.Client("oceanic-hangout-406022")

def load_dim_dates(date):
    #Checking if transformed data exists on GCS
    blob = bucket.blob(f'transformed/{date}_dim_dates.csv')
    if blob.exists() == False:
        return
    
    data = f"gs://outcomes_bucket/transformed/{date}_dim_dates.csv"
    table_id = "outcomes.dim_dates"
    try:
        client.get_table(table_id)
        #append data
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND",
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
        )
        load_job = client.load_table_from_uri(
            data, table_id, job_config=job_config
        ) 
        load_job.result()
    except NotFound:
        # create new table
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
        )
        load_job = client.load_table_from_uri(
            data, table_id, job_config=job_config
        )
        load_job.result()

def load_fct_outcomes(date):
    #Checking if transformed data exists on GCS
    blob = bucket.blob(f'transformed/{date}_fct_outcomes.csv')
    if blob.exists() == False:
        return

    data = f"gs://outcomes_bucket/transformed/{date}_fct_outcomes.csv"
    table_id = "outcomes.fct_outcomes"
    try:
        client.get_table(table_id)
        #append data
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND",
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
        )
        load_job = client.load_table_from_uri(
            data, table_id, job_config=job_config
        ) 
        load_job.result()
    except NotFound:
        # create new table
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
        )
        load_job = client.load_table_from_uri(
            data, table_id, job_config=job_config
        )
        load_job.result()

def load_dim_outcome_types(date):
    #Checking if transformed data exists on GCS
    blob = bucket.blob(f'transformed/{date}_dim_outcome_types.csv')
    if blob.exists() == False:
        return
    
    data = f"gs://outcomes_bucket/transformed/{date}_dim_outcome_types.csv"
    table_id = "outcomes.dim_outcome_types"

    try:
        client.get_table(table_id)
        # We don't want to update the table once the first day is loaded as the first load will have all the data and the subsequent ones will not.
    except NotFound:
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
        )
        load_job = client.load_table_from_uri(
            data, table_id, job_config=job_config
        )
        load_job.result()

def load_dim_animal():
    data = f"gs://outcomes_bucket/transformed/dim_animal_agg.csv"
    table_id = "outcomes.dim_animal"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
    )
    load_job = client.load_table_from_uri(
        data, table_id, job_config=job_config
    )
    load_job.result()

