from src.storage.postgres_store import create_connection

connection = create_connection()

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_database();")
        print(cursor.fetchone())
finally:
    connection.close()