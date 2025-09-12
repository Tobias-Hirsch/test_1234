from app.models.database import get_db, User
from datetime import timedelta, datetime, timezone

# Define the cleanup function
def remove_expired_unactivated_users():
    """Removes unactivated users whose activation tokens have expired."""
    print("Running scheduled cleanup of expired unactivated users...")
    db = next(get_db()) # Get a database session
    try:
        now = datetime.now()
        expired_users = db.query(User).filter(
            User.is_active == 0,
            User.activation_expires_at < now
        ).all()

        for user in expired_users:
            print(f"Deleting expired unactivated user: {user.username}")
            db.delete(user)

        db.commit()
        print(f"Cleanup complete. Removed {len(expired_users)} expired unactivated users.")
    except Exception as e:
        print(f"Error during scheduled cleanup: {e}")
        db.rollback() # Rollback changes in case of error
    finally:
        db.close() # Close the session