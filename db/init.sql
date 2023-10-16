CREATE TABLE IF NOT EXISTS outcome_dim (
    outcome_type_id INT PRIMARY KEY,
    outcome_type VARCHAR
);

CREATE TABLE IF NOT EXISTS sex_status_dim (
    sex_status_id INT PRIMARY KEY,
    sex_status VARCHAR
);

CREATE TABLE IF NOT EXISTS date_dim (
    date_id INT PRIMARY KEY,
    outcome_year INT,
    outcome_month INT,
    outcome_day INT
);

CREATE TABLE IF NOT EXISTS animal_dim (
    animal_id VARCHAR PRIMARY KEY,
    animal_name VARCHAR, --change ER diagrams accordingly
    animal_dob DATE,
    animal_type VARCHAR,
    animal_sex VARCHAR,
    animal_breed VARCHAR,
    animal_color VARCHAR
);

CREATE TABLE IF NOT EXISTS outcomes_fact (
    outcome_id SERIAL PRIMARY KEY,
    animal_id VARCHAR REFERENCES animal_dim(animal_id),
    date_id INT REFERENCES date_dim(date_id),
    outcome_type_id INT REFERENCES outcome_dim(outcome_type_id),
    sex_status_id INT REFERENCES sex_status_dim(sex_status_id)
);