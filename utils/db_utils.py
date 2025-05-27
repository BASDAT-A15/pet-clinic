import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()  

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv("dbname"),
        user=os.getenv("user"),
        password=os.getenv("password"),
        host=os.getenv("host"),
        port=os.getenv("port"),
        sslmode=os.getenv("require")
    )

    with conn.cursor() as cur:
        cur.execute("SET search_path TO %s", (os.getenv("schema"),))
    conn.commit()
    return conn