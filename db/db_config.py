import os
from dotenv import load_dotenv

def load_env():
    production_path = '.env.prod'
    if os.path.exists(production_path):
        load_dotenv(production_path, override=True)
    else:
        print(f"Warning: {production_path} bulunamadı. Varsayılan olarak .env dosyası yüklenecek.")
        load_dotenv('.env', override=True)

load_env()

def get_db_connection_string():
    ENV = os.getenv("ENV", "production").lower()
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_SERVER = os.getenv("DB_SERVER")
    DB_PORT = os.getenv("DB_PORT") or "5432"
    DB_DATABASE = os.getenv("DB_DATABASE")

    missing_vars = []
    for var_name, var_value in {
        "DB_USERNAME": DB_USERNAME,
        "DB_PASSWORD": DB_PASSWORD,
        "DB_SERVER": DB_SERVER,
        "DB_PORT": DB_PORT,
        "DB_DATABASE": DB_DATABASE,
    }.items():
        if not var_value:
            missing_vars.append(var_name)
    if missing_vars:
        raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")

    base_conn_str = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}:{DB_PORT}/{DB_DATABASE}"

    if ENV == "development":
        return base_conn_str
    else:
        return base_conn_str + "?sslmode=require"

