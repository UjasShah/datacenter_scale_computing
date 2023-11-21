FROM python 

WORKDIR /app
COPY etl.py etl.py

RUN pip install pandas psycopg2-binary sodapy

ENTRYPOINT [ "python", "etl.py"]