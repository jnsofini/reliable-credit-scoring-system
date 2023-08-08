import pandas as pd
from sqlalchemy import create_engine
import os
  
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
POSTGRES_USER = os.getenv("POSTGRES_USER","postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD","password")
data_base = os.getenv("data_base","test-db")

# Connection: postgresql+psycopg://user:password@host:port/dbname[?key=value&key=value...]

def db_connection_string(data_base: str):
    sync_engine = f"""postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{data_base}"""
    return sync_engine

def insert_dataframe(table_name: str, table_data: pd.DataFrame, conn_str: str | None = None, data_base: str = ""):
    sync_engine = conn_str or db_connection_string(data_base=data_base)
    db = create_engine(sync_engine)

    with db.connect() as conn:
        print("connection established:")
        table_data.to_sql(table_name, con=conn, if_exists='replace', index=False)
        print("Finished inserting!")

if __name__ == "__main__":
    # our dataframe
    data = pd.DataFrame(
        {
            'Name': ['Tom', 'dick', 'harry'],
            'Age': [22, 21, 24]
        }
        )
    
    insert_dataframe("Age", data=data, data_base=data_base)
