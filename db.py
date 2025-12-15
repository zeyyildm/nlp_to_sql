import psycopg2
import pandas as pd

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="nlp_sql_db",
        user="zeynepyildirim",
        password=""  # şifre varsa buraya yaz
    )

def run_query(sql):
    conn = get_connection()
    df = pd.read_sql(sql, conn)
    conn.close()
    return df
