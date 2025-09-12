import os
from pymongo import MongoClient
from typing import Dict, Any, List, Optional
from ..core.config import settings # Global import

MONGO_URI = settings.MONGO_URI
MONGO_DB_NAME = settings.MONGO_DB_NAME
MONGO_AI_CHAT_HISTORY_COLLECTION=settings.MONGO_AI_CHAT_HISTORY_COLLECTION

def get_mongo_client(mongo_uri: Optional[str] = None) -> MongoClient:
    """
    Connects to MongoDB and returns a MongoClient instance.
    Uses MONGO_URI from environment variables by default.
    """
    uri = mongo_uri if mongo_uri is not None else MONGO_URI
    if not uri:
        raise ValueError("MongoDB URI not provided and MONGO_URI environment variable is not set.")
    try:
        client = MongoClient(uri)
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        print("Connected to MongoDB successfully!")
        return client
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise

def get_database(client: MongoClient, db_name: Optional[str] = None):
    """
    Gets a specific database from the MongoDB client.
    Uses MONGO_DB_NAME from environment variables by default.
    """
    name = db_name if db_name is not None else MONGO_DB_NAME
    if not name:
        raise ValueError("MongoDB database name not provided and MONGO_DB_NAME environment variable is not set.")
    return client[name]

def insert_document(collection, document: Dict[str, Any]):
    """
    Inserts a single document into a MongoDB collection.
    """
    try:
        result = collection.insert_one(document)
        print(f"Inserted document with ID: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        print(f"Error inserting document: {e}")
        raise

def find_document(collection, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Finds a single document in a MongoDB collection.
    """
    try:
        document = collection.find_one(query)
        return document
    except Exception as e:
        print(f"Error finding document: {e}")
        raise

def find_documents(collection, query: Dict[str, Any], limit: int = 0) -> List[Dict[str, Any]]:
    """
    Finds multiple documents in a MongoDB collection.
    """
    try:
        cursor = collection.find(query)
        if limit > 0:
            cursor = cursor.limit(limit)
        documents = list(cursor)
        return documents
    except Exception as e:
        print(f"Error finding documents: {e}")
        raise

def update_document(collection, query: Dict[str, Any], update: Dict[str, Any]):
    """
    Updates a single document in a MongoDB collection.
    """
    try:
        result = collection.update_one(query, {"$set": update})
        print(f"Matched {result.matched_count} document(s) and modified {result.modified_count} document(s).")
        return result.modified_count
    except Exception as e:
        print(f"Error updating document: {e}")
        raise

def delete_document(collection, query: Dict[str, Any]):
    """
    Deletes a single document from a MongoDB collection.
    """
    try:
        result = collection.delete_one(query)
        print(f"Deleted {result.deleted_count} document(s).")
        return result.deleted_count
    except Exception as e:
        print(f"Error deleting document: {e}")
        raise

# Example Usage (optional, for testing)
if __name__ == "__main__":
    try:
        # Ensure MONGO_URI and MONGO_DB_NAME are set in your .env for this example
        client = get_mongo_client()
        db = get_database(client)

        # Example: Insert a document
        test_collection = db["test_collection"]
        test_document = {"name": "Test Document", "value": 123}
        inserted_id = insert_document(test_collection, test_document)

        # Example: Find the document
        found_doc = find_document(test_collection, {"_id": inserted_id})
        print(f"Found document: {found_doc}")

        # Example: Update the document
        update_document(test_collection, {"_id": inserted_id}, {"value": 456})
        updated_doc = find_document(test_collection, {"_id": inserted_id})
        print(f"Updated document: {updated_doc}")

        # Example: Delete the document
        delete_document(test_collection, {"_id": inserted_id})
        deleted_doc = find_document(test_collection, {"_id": inserted_id})
        print(f"Document after deletion: {deleted_doc}")

    except Exception as e:
        print(f"Example usage failed: {e}")
    finally:
        # Close the connection
        if 'client' in locals() and client:
            client.close()
            print("MongoDB connection closed.")