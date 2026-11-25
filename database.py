import psycopg2

conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    database=os.getenv("DB_NAME", "First project"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD")
)

if __name__ == "__main__":

    try:
        conn = get_connection()

        print("PostgreSQL Connected Successfully!")

        conn.close()

    except Exception as e:
        print("Connection Error:", e)

