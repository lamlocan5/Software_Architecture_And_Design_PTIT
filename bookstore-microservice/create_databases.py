import os
import sys

# Try to read credentials from .env
db_host = 'localhost'
db_port = '5432'
db_user = 'postgres'
db_password = '1234'

mysql_host = 'localhost'
mysql_port = 3306
mysql_user = 'root'
mysql_password = '123456789'

if os.path.exists('.env'):
    print("Reading connection details from .env...")
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key == 'DB_HOST':
                    db_host = val
                elif key == 'DB_PORT':
                    db_port = val
                elif key == 'DB_USER':
                    db_user = val
                elif key == 'DB_PASSWORD':
                    db_password = val
                elif key == 'MYSQL_HOST':
                    mysql_host = val
                elif key == 'MYSQL_PORT':
                    mysql_port = int(val)
                elif key == 'MYSQL_USER':
                    mysql_user = val
                elif key == 'MYSQL_PASSWORD':
                    mysql_password = val

# When running on host, host.docker.internal translates to localhost
if db_host == 'host.docker.internal':
    db_host = 'localhost'
if mysql_host == 'host.docker.internal':
    mysql_host = 'localhost'

pg_databases = [
    "bookstore_gateway",
    "bookstore_product",
    "bookstore_cart",
    "bookstore_order",
    "bookstore_review",
    "bookstore_catalogue",
    "bookstore_shipping",
    "bookstore_payment",
    "bookstore_ai",
    "bookstore_notification",
    "bookstore_frontend"
]

print("--- Checking PostgreSQL Databases ---")
print(f"Connecting to host PostgreSQL at {db_host}:{db_port} as user '{db_user}'...")

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
except ImportError:
    print("psycopg2 is not installed. Installing psycopg2-binary...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

has_error = False

try:
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        database="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Get list of existing databases
    cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
    existing_dbs = [row[0] for row in cursor.fetchall()]
    
    for db in pg_databases:
        if db in existing_dbs:
            print(f"Database '{db}' already exists.")
        else:
            print(f"Creating database '{db}'...")
            cursor.execute(f'CREATE DATABASE {db};')
            print(f"Database '{db}' created successfully.")
            
    cursor.close()
    conn.close()
    print("All PostgreSQL databases checked/created successfully!")
except Exception as e:
    print(f"Error connecting to or creating databases on PostgreSQL: {e}")
    has_error = True

print("\n--- Checking MySQL Databases ---")
print(f"Connecting to host MySQL at {mysql_host}:{mysql_port} as user '{mysql_user}'...")

try:
    import pymysql
except ImportError:
    print("pymysql is not installed. Installing pymysql...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pymysql"])
    import pymysql

try:
    mysql_conn = pymysql.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password
    )
    mysql_conn.autocommit(True)
    mysql_cursor = mysql_conn.cursor()
    
    mysql_cursor.execute("SHOW DATABASES;")
    existing_mysql_dbs = [row[0].lower() for row in mysql_cursor.fetchall()]
    
    db_name = "bookstore_user"
    if db_name in existing_mysql_dbs:
        print(f"MySQL database '{db_name}' already exists.")
    else:
        print(f"Creating MySQL database '{db_name}'...")
        mysql_cursor.execute(f"CREATE DATABASE {db_name};")
        print(f"MySQL database '{db_name}' created successfully.")
        
    mysql_cursor.close()
    mysql_conn.close()
    print("All MySQL databases checked/created successfully!")
except Exception as e:
    print(f"Error connecting to or creating databases on MySQL: {e}")
    print("Please make sure MySQL service is running on the host machine.")
    has_error = True

if has_error:
    sys.exit(1)
else:
    sys.exit(0)

