import psycopg2

def init_db():
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="123456",
        port=5432
    )
    cur = conn.cursor()
    with open('database/init_tables.sql', 'r') as f:
        sql_script = f.read()
    cur.execute(sql_script)
    conn.commit()
    cur.close()
    conn.close()
    print("Tables created successfully.")

if __name__ == "__main__":
    init_db()

