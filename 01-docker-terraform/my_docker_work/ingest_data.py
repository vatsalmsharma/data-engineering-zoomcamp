#!/usr/bin/env python
# coding: utf-8

import argparse
from time import time
import os

import pandas as pd
from sqlalchemy import create_engine
import pyarrow.parquet as pq

# pip install psycopg2
# 

def main(params):

    user = params.user
    password = params.password
    host = params.host 
    port = params.port
    database_name = params.database_name
    table_name = params.table_name
    url_csv = params.url_csv
    url_parquet = params.url_parquet
    table_name_par = params.table_name_par
    file_type = params.file_type

    csv_name = 'output_file.csv'
    parquet_name = 'output_file.parquet'
    # Download the data file
    # os.system(f"wget {url_csv} -O {csv_name}")
    # os.system(f"wget {url_parquet} -O {parquet_name}")

    # postgressql://<user_name>:<password>@<host>:<port>/<database>
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database_name}')
    engine.connect()

    if file_type == 'c':
        if url_csv.endswith('.csv.gz'):
            csv_name = 'output_file.csv.gz'
        else:
            csv_name = 'output_file.csv'
        os.system(f"wget {url_csv} -O {csv_name}")
    
        df = pd.read_csv(csv_name, nrows=100)
        # print(pd.io.sql.get_schema(df, name='yellow_taxi_data', con=engine))

        # To load data we will chunk the data using 'iterators'
        df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)


        # Lets create table (and no data loading)

        # dataframe.to_sql() will add the data from dataframe to the table
        # dataframe.to_sql(name=<database_name>, con=engine, if_exists='replace')

        df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

        # get_ipython().run_line_magic('time', "df.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')")
        # To load all the chunks

        while True:
            try:
                start_ts = time()
                df = next(df_iter)
                
                df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
                df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
                
                
                df.to_sql(name=table_name, con=engine, if_exists='append')
                
                end_ts = time()
                print('Next chunk data inserted/appended in %.3f seconds.' %(end_ts - start_ts))
            except StopIteration:
                print("Reached the end of the iteration.")
                break

    if file_type == 'p':
        os.system(f"wget {url_parquet} -O {parquet_name}")
        # Read metadata 
        # pq.read_metadata('dataset/yellow_tripdata_2025-01.parquet')


        # Read file, read the table from file and check schema
        file = pq.ParquetFile(parquet_name)
        table = file.read()
        table.schema


        # Convert to pandas and check data 
        pq_df = table.to_pandas()
        # pq_df.info()

        # Creating batches of 100,000 for the paraquet file
        batches_iter = file.iter_batches(batch_size=100000)
        # batches_iter

        # Insert values into the table 
        t_start = time()
        count = 0

        for batch in file.iter_batches(batch_size=100000):
            count+=1
            batch_df = batch.to_pandas()
            print(f'inserting batch {count}...')
            b_start = time()
            
            batch_df.to_sql(name=table_name_par,con=engine, if_exists='append')
            b_end = time()
            print(f'inserted! time taken {b_end-b_start:10.3f} seconds.\n')
            
        t_end = time()   
        print(f'Completed! Total time taken was {t_end-t_start:10.3f} seconds for {count} batches.')   


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest data to Postgres')

    parser.add_argument('--user', help='user name of postgres')
    parser.add_argument('--password', help='user name of postgres')
    parser.add_argument('--host', help='host of postgres')
    parser.add_argument('--port', help='port of postgres')
    parser.add_argument('--database_name', help='database name of postgres')
    parser.add_argument('--table_name', help='table name of postgres')
    parser.add_argument('--url_csv', help='url of csv file')
    parser.add_argument('--url_parquet', help='url of parquet file')
    parser.add_argument('--table_name_par', help='table name for 2nd table')
    parser.add_argument('--file_type', help='type_of_file')

    args = parser.parse_args()

    main(args)
    # Run It Up