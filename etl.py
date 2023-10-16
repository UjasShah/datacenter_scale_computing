# import argparse
import pandas as pd
import psycopg2

print('Starting ETL script')

url = "https://shelterdata.s3.amazonaws.com/shelter1000_new.csv"
df = pd.read_csv(url)

#check if animal_id is valid values
assert df['animal_id'].isnull().sum() == 0

# splitting sex into sex and sex_status by the space
df[['sex_status', 'sex']] = df['sex'].str.split(' ', expand=True)

# check if any names start with '*'
assert len(df[df['name'].str[0] == '*']) == 0

# convert ts to datetime
df['ts'] = pd.to_datetime(df['ts'])

# delete month_year column
del df['month_year']

# convert dob to date
df['dob'] = pd.to_datetime(df['dob'])

# see if values in outcome are valid
assert len(df['outcome'].unique()) == 7

# checking if values in type are as expected
assert len(df['type'].unique()) == 4

# convert all nulls to empty string
df = df.fillna('')

# creating outcome_dim table
outcome_dim = df.outcome.value_counts().reset_index().reset_index().loc[:, ['index', 'outcome']].rename(columns={'index': 'outcome_type_id', 'outcome': 'outcome_type'})

# creating sex_status_dim table
sex_status_dim = df.sex_status.value_counts().reset_index().reset_index().loc[:,['index','sex_status']]
sex_status_dim.columns = ['sex_status_id', 'sex_status']

#creating date_dim table
date_dim = df.ts.dt.date.value_counts().reset_index().loc[:,['ts']]
date_dim.columns = ['date_id']
date_dim[['outcome_year','outcome_month','outcome_day']] = date_dim['date_id'].astype(str).str.split('-', expand=True)
date_dim['date_id'] = date_dim['outcome_year'] + date_dim['outcome_month'] + date_dim['outcome_day']
date_dim.date_id = date_dim.date_id.astype('int')

#creating animal_dim table
temp = df.sort_values(by=['ts']).drop_duplicates(subset=['animal_id'], keep='last')

animal_dim = df.animal_id.value_counts().reset_index().loc[:,['animal_id']]
animal_dim = pd.merge(animal_dim, temp[['animal_id','name', 'dob','type','sex','breed','color']], on='animal_id', how='left')
animal_dim

# #creating outcome_fact table
outcomes_fact = df.loc[:,['animal_id','ts','outcome', 'sex_status']]
outcomes_fact.ts = outcomes_fact.ts.dt.date.astype(str).str.replace('-','').astype(int)
outcomes_fact = pd.merge(outcomes_fact, outcome_dim, left_on = 'outcome', right_on = 'outcome_type', how='left')
outcomes_fact = pd.merge(outcomes_fact, sex_status_dim, on='sex_status', how='left')
outcomes_fact.drop(columns= ['outcome_type', 'outcome','sex_status'], inplace=True)
outcomes_fact.rename(columns={'ts':'date_id'}, inplace=True)
outcomes_fact = pd.merge(outcomes_fact, animal_dim[['animal_id', 'dob']], on='animal_id', how='left')
outcomes_fact['age_on_outcome'] = ((pd.to_datetime(outcomes_fact.date_id.astype(str)) - outcomes_fact.dob) / pd.Timedelta(days=365.2425)).astype(int)
outcomes_fact.drop(columns=['dob'], inplace=True)


conn = psycopg2.connect(
    host="db",
    database="shelter_db",
    user="ujas",
    password="postgres_pass"
)

cur = conn.cursor()

for index, row in outcome_dim.iterrows():
    cur.execute(
        "INSERT INTO outcome_dim (outcome_type_id, outcome_type) VALUES (%s, %s)",
        (row['outcome_type_id'], row['outcome_type']))

for index, row in sex_status_dim.iterrows():
    cur.execute(
        "INSERT INTO sex_status_dim (sex_status_id, sex_status) VALUES (%s, %s)",
        (row['sex_status_id'], row['sex_status']))
    
for index, row in date_dim.iterrows():
    cur.execute(
        "INSERT INTO date_dim (date_id, outcome_year, outcome_month, outcome_day) VALUES (%s, %s, %s, %s)",
        (row['date_id'], row['outcome_year'], row['outcome_month'], row['outcome_day']))
    
for index, row in animal_dim.iterrows():
    cur.execute(
        "INSERT INTO animal_dim (animal_id, animal_name, animal_dob, animal_type, animal_sex, animal_breed, animal_color) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (row['animal_id'], row['name'], row['dob'], row['type'], row['sex'], row['breed'], row['color']))
    
for index, row in outcomes_fact.iterrows():
    cur.execute(
        "INSERT INTO outcomes_fact (animal_id, date_id, outcome_type_id, sex_status_id, age_on_outcome) VALUES (%s, %s, %s, %s, %s)",
        (row['animal_id'], row['date_id'], row['outcome_type_id'], row['sex_status_id'], row['age_on_outcome']))

    
conn.commit()
cur.close()
conn.close()


# parser = argparse.ArgumentParser(description = 'This is my first script to do something within a docker')

# parser.add_argument('-a', '--csv_to_read', type = str, help = 'This is the path to the csv file to read')
# parser.add_argument('-b', '--csv_to_write', type = str, help = 'This is the path to the csv file to write')

# args = parser.parse_args()

# df = pd.read_csv(args.csv_to_read)

# output = df['Outcome Type'].value_counts(normalize=True, dropna=False).reset_index()

# output.to_csv(args.csv_to_write, index = False)

print('Finished ETL script')