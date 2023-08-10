
import psycopg
import pandas as pd
from sqlalchemy import create_engine
import os

table = "test_table"
dummy_create_table_statement = f"""
drop table if exists {table};
create table {table}(
	index integer,
	psi float,
	bin VARCHAR
)
"""

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
POSTGRES_USER = os.getenv("POSTGRES_USER","postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD","password")
data_base = os.getenv("data_base","test-db")

# Connection: postgresql+psycopg://user:password@host:port/dbname[?key=value&key=value...]

def db_connection_string(data_base: str = ""):
    if data_base == "":
        return None
    sync_engine = f"""postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{data_base}"""
    return sync_engine


def prepare_database(conn_str:str | None = None, dbname="test", create_table_: str | None = None):
    conn_str = conn_str 

    """Create database if it doesn't exist."""
    with psycopg.connect(conn_str, autocommit=True) as conn:
        res = conn.execute(f"SELECT 1 FROM pg_database WHERE datname='{dbname}'")
        if len(res.fetchall()) == 0:
            conn.execute(f"create database {dbname};")
        with psycopg.connect(f"{conn_str} dbname={dbname}") as conn:
            create_table_ = create_table_ or dummy_create_table_statement
            conn.execute(create_table_)



def insert_dataframe(table_name: str, table_data: pd.DataFrame, conn_str: str | None = None, data_base: str = ""):
    if conn_str is None:
        raise Exception("No connection provided")
  
    db = create_engine(conn_str)

    with db.connect() as conn:
        print("connection established:")
        table_data.to_sql(table_name, con=conn, if_exists='replace', index=False)
        print("Finished inserting!")

if __name__ == "__main__":
    # our dataframe
    data_base = os.getenv("data_base","test-db")
    data = pd.DataFrame(
        {
            'Name': ['Tom', 'dick', 'harry'],
            'Age': [22, 21, 24]
        }
        )
    
    insert_dataframe("Age", table_data=data, data_base=data_base)