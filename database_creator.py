import pandas as pd
from sqlalchemy import create_engine

'''df=pd.read_csv('companies_sorted.csv')
df = df[df['industry'].notna()]
df = df[df['country'].notna()]
print('Loading in to database...')
engine = create_engine('postgresql://postgres:postgres@localhost:5432/company')
df.to_sql('tbl_companies', engine)'''

df = pd.DataFrame()
for chunk in pd.read_csv('companies_sorted.csv', chunksize=500):
    chunk = chunk[chunk['industry'].notna()]
    chunk = chunk[chunk['country'].notna()]
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/company')
    chunk.to_sql('tbl_companies', engine)