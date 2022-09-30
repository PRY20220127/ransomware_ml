import csv
import pandas as pd
from sqlalchemy import create_engine, types

engine = create_engine('mysql://ramsonware:server77VM@localhost/data_source') # enter your password and database names here

df = pd.read_csv("dataset2.csv",sep=';',quotechar='\'',encoding='utf8') # Replace Excel_file_name with your excel sheet name
df.fillna(value=0, inplace=True)
df.replace('N/A', 0, inplace=True)
df.replace('', 0, inplace=True)
df.to_sql('data',con=engine,index=True,if_exists='replace', index_label='ID') # Replace Table_name with your sql table name
