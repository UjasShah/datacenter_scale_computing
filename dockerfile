FROM python 

WORKDIR /app
COPY script.py script.py

RUN pip install pandas

ENTRYPOINT [ "python", "script.py"]