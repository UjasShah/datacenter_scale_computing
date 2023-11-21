import pandas as pd
from sqlalchemy import create_engine
import os
from sqlalchemy.dialects.postgresql import insert

def load_data(table_file, table_name, key):
    # DB connection string specified in docker-compose
    db_url = os.environ['DB_URL']
    conn = create_engine(db_url)

    def insert_on_conflict_nothing(table, conn, keys, data_iter):
        # "key" is the primary key in "conflict_table"
        data = [dict(zip(keys, row)) for row in data_iter]
        stmt = insert(table.table).values(data).on_conflict_do_nothing(index_elements=[key])
        result = conn.execute(stmt)
        return result.rowcount

    # load all the data in a loop
    pd.read_parquet(table_file).to_sql(table_name, conn, if_exists="append", index=False, method=insert_on_conflict_nothing)
    print(table_name+" loaded")

def load_fact_data(table_file, table_name):
    # DB connection string specified in docker-compose
    db_url = os.environ['DB_URL']
    conn = create_engine(db_url)

    
    pd.read_parquet(table_file).to_sql(table_name, conn, if_exists="replace", index=False)
    print(table_name+" loaded")