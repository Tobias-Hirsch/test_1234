import json
import logging
from sqlalchemy.orm import Session
from app.models.database import get_db, Policy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transform_subjects(subjects: list) -> list:
    """Transforms the old subjects format to the new AttributeFilter format."""
    if not isinstance(subjects, list) or not subjects:
        return subjects

    if isinstance(subjects[0], dict) and 'key' in subjects[0] and 'operator' in subjects[0]:
        logger.info("Subjects already in new format. Skipping transformation.")
        return subjects

    new_subjects = []
    for subject in subjects:
        if isinstance(subject, dict) and 'role' in subject:
            new_subjects.append({
                "key": "user.roles",
                "operator": "in",
                "value": [subject['role']]
            })
    return new_subjects

def transform_resources(resources: list) -> list:
    """Transforms the old resources format to the new AttributeFilter format."""
    if not isinstance(resources, list) or not resources:
        return resources

    if isinstance(resources[0], dict) and 'key' in resources[0] and 'operator' in resources[0]:
        logger.info("Resources already in new format. Skipping transformation.")
        return resources

    new_resources = []
    for resource in resources:
        if isinstance(resource, str):
            new_resources.append({
                "key": "resource.type",
                "operator": "in",
                "value": [resource]
            })
    return new_resources

def migrate_policies_data(db: Session):
    """
    Migrates all existing policies in the database from the old data structure
    to the new one.
    """
    logger.info("Starting policy data migration...")
    try:
        all_policies = db.query(Policy).all()
        if not all_policies:
            logger.info("No policies found to migrate.")
            return

        for policy in all_policies:
            logger.info(f"Migrating policy ID: {policy.id}, Name: {policy.name}")

            # Transform subjects
            original_subjects = policy.subjects
            new_subjects_json = transform_subjects(original_subjects)
            if new_subjects_json != original_subjects:
                policy.subjects = new_subjects_json
                logger.info(f"  - Transformed subjects for policy {policy.id}")

            # Transform resources
            original_resources = policy.resources
            new_resources_json = transform_resources(original_resources)
            if new_resources_json != original_resources:
                policy.resources = new_resources_json
                logger.info(f"  - Transformed resources for policy {policy.id}")

        db.commit()
        logger.info("Policy data migration completed successfully.")

    except Exception as e:
        logger.error(f"An error occurred during policy migration: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Get a database session
    db_session = next(get_db())
    # Run the migration
    migrate_policies_data(db_session)