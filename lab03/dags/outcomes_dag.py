from airflow.operators.python_operator import PythonOperator
from airflow import DAG
from datetime import datetime
from etl_scripts.extract import extract_data

with DAG(
    dag_id="outcomes_dag",
    start_date=datetime(2023, 11, 18),
    schedule_interval="@daily",
    max_active_runs=1
) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=extract_data,
        op_kwargs={"date": "{{ ds }}"}
)
    
    extract
