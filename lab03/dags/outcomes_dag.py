from airflow.operators.python_operator import PythonOperator
from airflow import DAG
from datetime import datetime
from etl_scripts.extract import extract_data
from etl_scripts.transform import transform_data
from etl_scripts.load import load_dim_dates
from etl_scripts.load import load_fct_outcomes
from etl_scripts.load import load_dim_outcome_types
from etl_scripts.load import load_dim_animal

with DAG(
    dag_id="outcomes_dag",
    start_date=datetime(2023, 11, 1),
    schedule_interval="@daily",
    max_active_runs=1 # to help my potato laptop
) as dag:

    extract = PythonOperator(
        task_id="extract",
        python_callable=extract_data,
        op_kwargs={"date": "{{ ds }}"}
)
    
    transform = PythonOperator(
        task_id="transform",
        python_callable=transform_data,
        op_kwargs = {"date": "{{ ds }}"}
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
    
    extract >> transform >> [load_dates_dim, load_outcomes_fct, load_outcome_types_dim, load_animal_dim]
