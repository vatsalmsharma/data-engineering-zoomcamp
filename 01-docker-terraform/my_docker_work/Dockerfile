FROM python:3.11
# FROM tell the base image we want to use 

RUN apt-get install wget
RUN pip install pandas sqlalchemy psycopg2 pyarrow

WORKDIR /app
# COPY pipeline.py pipeline.py
COPY ingest_data.py ingest_data.py

# ENTRYPOINT [ "bash" ]
# ENTRYPOINT [ "python", "pipeline.py" ]
ENTRYPOINT [ "python", "ingest_data.py" ]
