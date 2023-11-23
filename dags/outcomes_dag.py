from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from etl_scripts.transform import transform_data
from etl_scripts.load import load_data, load_fact_data
from datetime import datetime
import os

SOURCE_URL = 'https://data.austintexas.gov/api/views/9t4d-g238/rows.csv'
AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", '/opt/airflow')
CSV_TARGET_DIR = AIRFLOW_HOME + '/data/{{ ds }}/downloads'
CSV_TARGET_FILE = CSV_TARGET_DIR + '/outcomes.csv'

with DAG (
    dag_id = "outcomes_dag",
    start_date = datetime(2023, 11, 20),
    schedule_interval = "@daily"
) as dag:
    
    extract = BashOperator(
        task_id="extract",
        bash_command=f"curl --create-dirs -o {CSV_TARGET_FILE} {SOURCE_URL}"
    )

    transform = PythonOperator(
        task_id="transform",
        python_callable=transform_data,
        op_kwargs = {
            'source_csv': CSV_TARGET_FILE,
            'target_dir': AIRFLOW_HOME + '/data/{{ ds }}/transformed'
        }
    )

    load_animals_dim = PythonOperator(
        task_id="load_animals_dim",
        python_callable=load_data,
        op_kwargs = {
            'table_file': AIRFLOW_HOME + '/data/{{ ds }}/transformed/dim_animals.parquet',
            'table_name': 'dim_animals',
            'key': 'animal_id'
        }
    )

    load_dates_dim = PythonOperator(
        task_id="load_dates_dim",
        python_callable=load_data,
        op_kwargs = {
            'table_file': AIRFLOW_HOME + '/data/{{ ds }}/transformed/dim_dates.parquet',
            'table_name': 'dim_dates',
            'key': 'date_id'
        }
    )

    load_outcomes_dates_dim = PythonOperator(
        task_id="load_outcome_types_dim",
        python_callable=load_data,
        op_kwargs = {
            'table_file': AIRFLOW_HOME + '/data/{{ ds }}/transformed/dim_outcome_types.parquet',
            'table_name': 'dim_outcome_types',
            'key': 'outcome_type_id'
        }
    )

    load_outcome_fact = PythonOperator(
        task_id="load",
        python_callable=load_fact_data,
        op_kwargs = {
            'table_file': AIRFLOW_HOME + '/data/{{ ds }}/transformed/fct_outcomes.parquet',
            'table_name': 'fct_outcomes'
        }
    )

    extract >> transform >> [load_animals_dim, load_dates_dim, load_outcomes_dates_dim] >> load_outcome_fact