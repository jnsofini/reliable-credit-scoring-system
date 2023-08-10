# from monitoring import monitoring, db
import psycopg
import pandas as pd
from sqlalchemy import create_engine

from monitoring import db
  
  
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "password"
sync_engine = (
    f"postgresql+psycopg://{POSTGRES_USER}"
    f":{POSTGRES_PASSWORD}@{POSTGRES_HOST}"
    f":{POSTGRES_PORT}"
    )

dummy_create_table_statement = """
drop table if exists dummy_metrics;
create table dummy_metrics(
	timestamp timestamp,
	value1 integer,
	value2 varchar,
	value3 float
)
"""

CREATE_CONN_STRING = f"host={POSTGRES_HOST} port={POSTGRES_PORT} user={POSTGRES_USER} password={POSTGRES_PASSWORD}"

# def prepare_database(conn_string : str | None = None, dbname: str = "test", create_table_: str | None = None):

#     """Create database if it doesn't exist."""
#     with psycopg.connect(conn_string, autocommit=True) as conn:
#         res = conn.execute(f"SELECT 1 FROM pg_database WHERE datname='{dbname}'")
#         if len(res.fetchall()) == 0:
#             conn.execute(f"create database {dbname};")
        
#         # with psycopg.connect(f"{conn_string} dbname={dbname}") as conn:
#         #     create_table_ = create_table_ or dummy_create_table_statement
#         #     conn.execute(create_table_)
#     return dbname, conn_string

# def prepare_table(db_conn: str, create_table_: str | None = None):
#     with psycopg.connect(db_conn) as conn:
#         create_table_ = create_table_ or dummy_create_table_statement
#         conn.execute(create_table_)
    
#     return db_conn

def test_get_table_name():
    dummy_create_table_statement = """
    drop table if exists dummy_metrics;
    create table dummy_metrics(
        timestamp timestamp,
        value1 integer,
        value2 varchar,
        value3 float
    )
    """

    table_name = db.extract_from_create_statement(dummy_create_table_statement)
    print(table_name)
    assert table_name == "dummy_metrics"

def test_create_database():
    db_name, conn_string = db.prepare_database(conn_string=CREATE_CONN_STRING, dbname="test_db3")

    assert db_name == "test_db3"
    assert conn_string == CREATE_CONN_STRING
    # prepare_table

    
def test_create_table():
    table_name = db.prepare_table(
        db_conn=f"{CREATE_CONN_STRING} dbname=test_db3", 
        create_table_=dummy_create_table_statement
        )
    
    assert table_name == "dummy_metrics"

test_get_table_name()
    
# def test_create_db_and_table():
#      db_name, db_conn = db.prepare_database(
#         conn_string=CREATE_CONN_STRING, 
#         dbname="test_db4", 
#         create_table_=dummy_create_table_statement
#         )
#      prepare_table(
#         db_conn=f"{db_conn} dbname={db_name}", 
#         create_table_=dummy_create_table_statement
#         )
# test_create_database()
# test_create_table()
# Test both
# test_create_database()
# test_create_table()

# test_create_db_and_table()
# def test_insert_to_table():
#     data = pd.DataFrame(
#         {'Name': ['Tom', 'dick', 'harry'],
#         'Age': [22, 21, 24]}
#         )
#     db.insert_dataframe(
#         table_name=test_table, 
#         table_data=data,

#         )