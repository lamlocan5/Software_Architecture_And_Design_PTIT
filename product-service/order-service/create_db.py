import MySQLdb
import os
import sys
import time

DB_NAME = os.environ.get('MYSQL_DB', 'order_db')
HOST = os.environ.get('MYSQL_HOST', 'mysql_db')
USER = os.environ.get('MYSQL_USER', 'root')
PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
PORT = int(os.environ.get('MYSQL_PORT', 3306))

for i in range(30):
    try:
        conn = MySQLdb.connect(host=HOST, user=USER, password=PASSWORD, port=PORT)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Database '{DB_NAME}' ready.")
        sys.exit(0)
    except Exception as e:
        print(f"Waiting for MySQL... ({i+1}/30): {e}")
        time.sleep(2)

print("Failed to connect to MySQL after 30 attempts.")
sys.exit(1)
