import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table

load_dotenv()

# Database credentials from environment variables
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3307))
MYSQL_DB = os.getenv("MYSQL_DB", "rag_db")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")

# Construct the database URL
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

metadata = MetaData()

try:
    # Reflect the table to check if it exists
    file_gists_table = Table('file_gists', metadata, autoload_with=engine)
    print('Dropping table \'file_gists\'...')
    file_gists_table.drop(engine)
    print('Table \'file_gists\' dropped successfully.')
except Exception as e:
    print(f'Error dropping table \'file_gists\': {e}')
    print('Table might not exist or another error occurred.')