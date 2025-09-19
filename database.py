import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

def postgres_chatwoot():
    try:
        db_config = {
            'dbname': os.environ.get('POSTGRES_DB'),
            'user': os.environ.get('POSTGRES_USER'),
            'password': os.environ.get('POSTGRES_PASSWORD'),
            'host': os.environ.get('POSTGRES_HOST'),
            'port': os.environ.get('POSTGRES_PORT')
        }
        conn = psycopg2.connect(**db_config, cursor_factory=psycopg2.extras.DictCursor)
        cur = conn.cursor()
        return conn, cur
    except Exception as e:
        print(f"Error connecting to Postgres: {e}")
        raise
    
def postgres_site():
    try:
        db_config = {
            'dbname': os.environ.get('POSTGRES_SITE_DB'),
            'user': os.environ.get('POSTGRES_SITE_USER'),
            'password': os.environ.get('POSTGRES_SITE_PASSWORD'),
            'host': os.environ.get('POSTGRES_SITE_HOST'),
            'port': os.environ.get('POSTGRES_SITE_PORT')
        }
        conn = psycopg2.connect(**db_config, cursor_factory=psycopg2.extras.DictCursor)
        cur = conn.cursor()
        return conn, cur
    except Exception as e:
        print(f"Error connecting to Postgres: {e}")
        raise
    