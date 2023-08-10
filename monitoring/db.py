
import psycopg
import pandas as pd
from sqlalchemy import create_engine
import os
import re

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
data_base = os.getenv("data_base","test_db")

# Connection: postgresql+psycopg://user:password@host:port/dbname[?key=value&key=value...]

def db_sync_connection_string(data_base: str = ""):
    """Connection string to insert data dataframe to posgres"""
    if data_base == "":
        return None
    sync_engine = f"""postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{data_base}"""
    return sync_engine

def prepare_database(conn_string : str, dbname: str = "test"):

    """Create database if it doesn't exist."""
    with psycopg.connect(conn_string, autocommit=True) as conn:
        res = conn.execute(f"SELECT 1 FROM pg_database WHERE datname='{dbname}'")
        if len(res.fetchall()) == 0:
            conn.execute(f"create database {dbname};")
        
        # with psycopg.connect(f"{conn_string} dbname={dbname}") as conn:
        #     create_table_ = create_table_ or dummy_create_table_statement
        #     conn.execute(create_table_)
    return dbname, conn_string

def prepare_table(db_conn: str, create_table_: str | None = None):
    with psycopg.connect(db_conn) as conn:
        create_table_ = create_table_ or dummy_create_table_statement
        conn.execute(create_table_)

    table_name = extract_from_create_statement(create_table_)
    return table_name

def prepare_database_and_table(conn_string : str , dbname: str = "test", create_table_: str | None = None):

    """Create database if it doesn't exist."""
    with psycopg.connect(conn_string, autocommit=True) as conn:
        res = conn.execute(f"SELECT 1 FROM pg_database WHERE datname='{dbname}'")
        if len(res.fetchall()) == 0:
            conn.execute(f"create database {dbname};")
        with psycopg.connect(f"{conn_string} dbname={dbname}") as conn:
            create_table_ = create_table_ or dummy_create_table_statement
            conn.execute(create_table_)

# def prepare_table(db_conn_string : str, dbname: str = "test"):
#     if not db_conn_string.endswith(f"/{dbname}"):
#         db_conn_string = 
#     with psycopg.connect(f"{db_conn_string} dbname={dbname}") as conn:
#             create_table_ = create_table_ or dummy_create_table_statement
#             conn.execute(create_table_)

def extract_from_create_statement(create_statement: str):
    """Extract table name from create statement."""

    # Define a regular expression pattern to match the "create table" statement
    pattern = r"create\s+table\s+(\w+)\s*\("

    # Search for the pattern in the SQL code
    match = re.search(pattern, create_statement, re.IGNORECASE)

    if match:
        table_name = match.group(1)
        return table_name
    
    return None




def insert_dataframe(table_name: str, table_data: pd.DataFrame, sync_engine: str | None = None):
    if sync_engine is None:
        raise Exception("No connection provided")
  
    db = create_engine(sync_engine)

    with db.connect() as conn:
        print("connection established:")
        table_data.to_sql(table_name, con=conn, if_exists='replace', index=False)
        print("Finished inserting!")

if __name__ == "__main__":
    # our dataframe
    data_base = os.getenv("data_base", "test_db")
    create_conn_string = f"host={POSTGRES_HOST} port={POSTGRES_PORT} user={POSTGRES_USER} password={POSTGRES_PASSWORD}"
    db_name, conn_string = prepare_database(
        conn_string=create_conn_string,
        dbname=data_base,
    )
    table_name = prepare_table(
        db_conn=f"{conn_string} dbname={db_name}",
        create_table_=dummy_create_table_statement
        )
                                            
    data = pd.DataFrame(
        {
            'Name': ['Tom', 'dick', 'harry'],
            'Age': [22, 21, 24]
        }
        )
    syn_engine_string = db_sync_connection_string(data_base=data_base)
    
    insert_dataframe("Age", table_data=data, sync_engine=syn_engine_string)