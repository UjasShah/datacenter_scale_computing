from airflow.operators.python_operator import PythonOperator
from airflow.providers.google.cloud.operators.dataproc import DataprocCreateClusterOperator, DataprocDeleteClusterOperator, DataprocSubmitJobOperator
from airflow import DAG, settings
from airflow.models.connection import Connection
from datetime import datetime
from etl_scripts.extract import extract_data
from etl_scripts.load import load_dim_dates
from etl_scripts.load import load_fct_outcomes
from etl_scripts.load import load_dim_outcome_types
from etl_scripts.load import load_dim_animal
from dotenv import load_dotenv

load_dotenv()

## I defined the connection in the UI, but I'm leaving this here for reference
# c = Connection(
#     conn_id="google_cloud_default",
#     conn_type="google_cloud_platform",
#     extra='{"extra__google_cloud_platform__key_path":"/opt/airflow/dags/etl_scripts/oceanic-hangout-406022-fd958fa4d302.json", "extra__google_cloud_platform__scope":"https://www.googleapis.com/auth/cloud-platform"}'
# )

# session = settings.Session()
# session.add(c)
# session.commit()

with DAG(
    dag_id="outcomes_dag",
    start_date=datetime(2023, 12, 18),
    schedule_interval="@daily",
    max_active_runs=1 # to help my potato laptop
) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=extract_data,
        op_kwargs={"date": "{{ ds }}"}
    )
    
    create_cluster = DataprocCreateClusterOperator(
        task_id="create_cluster",
        cluster_name="shelter-cluster",
        project_id="oceanic-hangout-406022",
        region="us-central1",
        cluster_config={
            'master_config': {
                'num_instances': 1,
                'machine_type_uri': 'n1-standard-2'
            },
            'worker_config': {
                'num_instances': 2,
                'machine_type_uri': 'n1-standard-2'
            }
        }
    )

    submit_pyspark_job = DataprocSubmitJobOperator(
        task_id="submit_pyspark_job",
        project_id="oceanic-hangout-406022",
        region="us-central1",
        cluster_name="shelter-cluster",
        job = {
            'placement': {'cluster_name': 'shelter-cluster'},
            'pyspark_job': {'main_python_file_uri': 'gs://outcomes_bucket/transform.py'}
        }
    )

    delete_cluster = DataprocDeleteClusterOperator(
        task_id="delete_cluster",
        cluster_name="shelter-cluster",
        project_id="oceanic-hangout-406022",
        region="us-central1"
    )

    load_dates_dim = PythonOperator(
        task_id="load_dates_dim",
        python_callable=load_dim_dates,
        op_kwargs = {"date": "{{ ds }}"}
    )

    load_outcomes_fct = PythonOperator(
        task_id="load_outcomes_fct",
        python_callable=load_fct_outcomes,
        op_kwargs = {"date": "{{ ds }}"}
    )
    
    load_outcome_types_dim = PythonOperator(
        task_id="load_outcome_types_dim",
        python_callable=load_dim_outcome_types,
        op_kwargs = {"date": "{{ ds }}"}
    )

    load_animal_dim = PythonOperator(
        task_id="load_animal_dim",
        python_callable=load_dim_animal
    )
    
    extract >> create_cluster >> submit_pyspark_job >> delete_cluster >> [load_dates_dim, load_outcomes_fct, load_outcome_types_dim, load_animal_dim]
