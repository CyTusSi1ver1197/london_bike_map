#!/usr/bin/env python
# coding: utf-8

import os
import sys
import psycopg2
import pandas as pd
import datetime as dt
import argparse
from io import StringIO
from time import time
from dotenv import load_dotenv



load_dotenv()
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASS")
host = os.getenv("POSTGRES_HOST") 
port = os.getenv("POSTGRES_PORT") 
db = os.getenv("POSTGRES_DB")
db_schema = os.getenv("POSTGRES_DB_SCHEMA")
table_name = os.getenv("POSTGRES_TABLE")
url = os.getenv("URL")

param_dic = {
"host"      : host,
"port"      : port,
"database"  : db,
"user"      : user,
"password"  : password,
"options"   : f"-c search_path=dbo,{db_schema}"
}


# Kudos to: NaysanSaran for connect() and copy_from_file() func
# Source: https://github.com/NaysanSaran/pandas2postgresql/blob/master/notebooks/Psycopg2_Bulk_Insert_Speed_Benchmark.ipynb
def connect(params_dic):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params_dic)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1) 
    print("Connection successful")
    return conn

def create_table(connection, dtypes, table_names):
    cursor = connection.cursor()
    print("Start creating table ... ")
    create_table_query = f'CREATE TABLE IF NOT EXISTS {table_names} ('
    for column, dtype in dtypes.items():
        create_table_query += f'"{column}" {dtype}, '
    create_table_query = create_table_query.rstrip(", ") + ")"
    cursor.execute(create_table_query)
    connection.commit()
    print(f"Done creating table: {table_names}")
    cursor.close()

def create_multi_tables(conn, dtypes, table_names: list):
    for table in table_names:
        create_table(conn, dtypes, table)

def copy_from_csv(conn, df, table):
    cur = conn.cursor()
    copy_query = """
            COPY {} FROM STDIN WITH CSV DELIMITER ',' NULL ''
            """.format(table)
    csv_data = StringIO()
    df.to_csv(csv_data, index_label='id', header = False)
    csv_data.seek(0)
    try:
        cur.copy_expert(sql=copy_query, file=csv_data)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error: %s" % error)
        conn.rollback()
        cur.close()
        return 1
    print("copy_from_csv() done")
    cur.close()

def find_first_day(year):
    d = dt.date(year, 1, 1)
    while d.weekday() != 2:  # Monday is represented by 0, Tues : 1 and so on
        d += dt.timedelta(1)
    return d

def generate_csv_name(start_year, end_year):
    id_2017 = 39
    id = (start_year - 2017)*52 + id_2017
    start_week = find_first_day(start_year)
    pre_date = "JourneyDataExtract"
    after_date = ".csv"
    str_List = []

    while(start_week.year != end_year+1):
        
        next_week = start_week + dt.timedelta(6)
        formatted_date_start = start_week.strftime("%d%b%Y")
        formatted_date_end = next_week.strftime("%d%b%Y")
        if(id >= 112):
            str_List.append(str(str(id) + pre_date + formatted_date_start +"-"+ formatted_date_end+after_date))
        start_week = next_week + dt.timedelta(1)
        id += 1
    
    return str_List



def main(args):   
    t_total_start = time()
    start_year = args.start
    end_year = args.end

    # Creating a list of filenames:
    file_List = generate_csv_name(int(start_year), int(end_year))

    # Table data types:
    bike_dtypes = {
        "Rental Id": pd.Int64Dtype(),	
        "Duration": pd.Int64Dtype(),
        "Bike Id": pd.Int64Dtype(),	
        "EndStation Id": pd.Int64Dtype(),	
        "EndStation Name": str, 
        "StartStation Id": pd.Int64Dtype(),	
        "StartStation Name": str 
    }

    parsing_dates = ["End Date", "Start Date"]

    bike_dtypes_postgres = {
        "Rental Id": "BIGINT",
        "Duration": "BIGINT",
        "Bike Id": "BIGINT",
        "End Date": "TIMESTAMP",
        "EndStation Id": "BIGINT",
        "EndStation Name": "TEXT",
        "Start Date": "TIMESTAMP",
        "StartStation Id": "BIGINT",
        "StartStation Name": "TEXT"
    }



    # Connect to database
    conn = connect(param_dic)

    # Create tables:
    table_List = []
    for i in range(int(start_year), int(end_year) + 1):
        table_List.append(f"{table_name}_{str(i)}")

    create_multi_tables(conn, bike_dtypes_postgres, table_List)

    for file in file_List:
        try:
            year = file.split('-')[0][-4:]
            total_path = url + file
            total_path = total_path.replace(" ", "%20")
        
            # Reading data files
            df = pd.read_csv(total_path, low_memory = False, dayfirst=True, index_col=0, dtype=bike_dtypes, parse_dates=parsing_dates)
            
            # Copying to database:
            t_start = time()
            copy_from_csv(conn, df, f"{table_name}_{year}")
            t_end = time()
            print('inserted {}, took {} second'.format(file, round(t_end - t_start,3)))
        except FileNotFoundError:
            continue

    t_total_end = time()
    print('Completed uploading data to postgres, took %.3f second' % (t_total_end - t_total_start))
    conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')
    parser.add_argument('--start', required=True, type = int, help='start year to collect data')
    parser.add_argument('--end', required=True, type = int, help='end year to collect data')

    args = parser.parse_args()

    main(args)