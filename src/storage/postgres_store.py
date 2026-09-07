import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def create_connection():
    return psycopg2.connect(
        host="localhost",
        port=os.getenv("DB_PORT_HOST", "5433"),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )

