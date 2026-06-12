import os
import sys

# Try to read credentials from one of the service env files or default to user values
db_host = 'localhost'
db_port = '5432'
db_user = 'postgres'
db_password = '1234'

databases = [
    "healthcare_patient",
    "healthcare_clinical",
    "healthcare_billing",
    "healthcare_inventory",
    "healthcare_doctor"
]

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
    
    for db in databases:
        if db in existing_dbs:
            print(f"Database '{db}' already exists. Recreating it to avoid migration conflicts...")
            try:
                cursor.execute(f"SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{db}' AND pid <> pg_backend_pid();")
            except Exception:
                pass
            cursor.execute(f'DROP DATABASE IF EXISTS {db};')
            cursor.execute(f'CREATE DATABASE {db};')
            print(f"Database '{db}' recreated successfully.")
        else:
            print(f"Creating database '{db}'...")
            cursor.execute(f'CREATE DATABASE {db};')
            print(f"Database '{db}' created successfully.")
            
    cursor.close()
    conn.close()
    print("All databases checked/created successfully!")
except Exception as e:
    print(f"Error connecting to or creating databases on PostgreSQL: {e}")
    sys.exit(1)
