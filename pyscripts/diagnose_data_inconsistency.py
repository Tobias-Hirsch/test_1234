import os
import sys
from pymilvus import utility, connections
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# --- Configuration ---
# Add the project root to the Python path to allow imports from 'app'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, project_root)

from backend.app.models.database import RagData, Base
from backend.app.core.config import settings

def diagnose():
    """
    Connects to MySQL and Milvus to find inconsistencies between RAG data entries
    and existing Milvus collections.
    """
    print("--- RAG Data Inconsistency Diagnostic Tool ---")

    # --- 1. Connect to MySQL ---
    try:
        print("\nConnecting to MySQL...")
        db_url = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}"
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        print("Successfully connected to MySQL.")
    except Exception as e:
        print(f"!!! ERROR: Could not connect to MySQL. Please check your .env settings.")
        print(f"Details: {e}")
        return

    # --- 2. Connect to Milvus ---
    try:
        print("\nConnecting to Milvus...")
        connections.connect("default", host=settings.MILVUS_HOST, port=settings.MILVUS_PORT)
        print(f"Successfully connected to Milvus at {settings.MILVUS_HOST}:{settings.MILVUS_PORT}.")
    except Exception as e:
        print(f"!!! ERROR: Could not connect to Milvus. Please check your .env settings and ensure the service is running.")
        print(f"Details: {e}")
        db.close()
        return

    # --- 3. Run Diagnostics ---
    print("\nFetching RAG items from database and checking against Milvus collections...")
    orphan_items = []
    found_items = []
    
    try:
        all_rag_items = db.query(RagData).all()
        if not all_rag_items:
            print("No RAG data entries found in the database.")
            return

        print(f"Found {len(all_rag_items)} RAG item(s) in the database. Checking each one...")

        for item in all_rag_items:
            # Sanitize name to create the expected collection name
            sanitized_name = item.name.lower().replace(" ", "_")
            collection_name = f"rag_{sanitized_name}"
            
            if utility.has_collection(collection_name):
                found_items.append(f"  - ID: {item.id}, Name: '{item.name}' -> Collection '{collection_name}' (OK)")
            else:
                orphan_items.append(f"  - ID: {item.id}, Name: '{item.name}' -> Collection '{collection_name}' (MISSING!)")

        # --- 4. Report Results ---
        print("\n--- Diagnostic Results ---")
        if found_items:
            print("\n[+] Found matching Milvus collections for these RAG items:")
            for f in found_items:
                print(f)
        
        if orphan_items:
            print("\n[!] The following RAG items are 'orphans'. They exist in the database but have NO matching Milvus collection:")
            for o in orphan_items:
                print(o)
            print("\nRecommendation: These orphan entries are likely causing the 'Collection does not exist' warnings.")
            print("You may need to delete these entries from the 'rag_data' table in your database or re-process the documents for them.")
        else:
            print("\n[+] All RAG items in the database have a corresponding Milvus collection. No inconsistencies found.")

    except Exception as e:
        print(f"\n!!! An error occurred during the diagnostic check: {e}")
    finally:
        # --- 5. Cleanup ---
        print("\nDisconnecting...")
        db.close()
        connections.disconnect("default")
        print("Diagnostic complete.")

if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()
    diagnose()