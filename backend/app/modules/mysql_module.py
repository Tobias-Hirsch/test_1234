import mysql.connector
from typing import List
from ..core.config import settings # Global import

MYSQL_HOST = settings.MYSQL_HOST
MYSQL_PORT = settings.MYSQL_PORT
MYSQL_USER = settings.MYSQL_USER
MYSQL_PASSWORD = settings.MYSQL_PASSWORD
MYSQL_DATABASE = settings.MYSQL_DATABASE

def store_metadata_in_mysql(filename: str, minio_url: str, milvus_ids: List[str]):
    try:
        # Connect to MySQL
        mydb = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )

        mycursor = mydb.cursor()

        # Create table if not exists
        mycursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255),
                minio_url VARCHAR(255),
                milvus_ids TEXT
            )
        """)

        # Prepare data for insertion
        milvus_ids_str = ",".join(milvus_ids)
        sql = "INSERT INTO documents (filename, minio_url, milvus_ids) VALUES (%s, %s, %s)"
        val = (filename, minio_url, milvus_ids_str)

        # Execute the query
        mycursor.execute(sql, val)

        # Commit the changes
        mydb.commit()

        print(mycursor.rowcount, "record inserted.")

    except Exception as e:
        print("Error occurred: ", e)
        raise